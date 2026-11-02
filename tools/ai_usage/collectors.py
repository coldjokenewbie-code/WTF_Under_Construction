"""Local authenticated CLI collectors. No raw command output is persisted."""
import json
import os
import selectors
import signal
import subprocess
import threading
import time

try:
    from .normalize import ParseError, parse_agy, parse_claude, parse_codex, utc_now
except ImportError:
    from normalize import ParseError, parse_agy, parse_claude, parse_codex, utc_now


COMMANDS = {
    # Quota probes must not load project/user hooks or MCP servers.
    'claude': ['claude', '-p', '/usage', '--tools', '', '--output-format', 'stream-json',
               '--verbose', '--setting-sources', '', '--strict-mcp-config'],
    'agy': ['agy', '--print', '/usage', '--output-format', 'json', '--print-timeout', '30s'],
    'codex': ['codex', 'app-server'],
}
LABELS = {'claude': 'Claude', 'agy': 'Antigravity', 'codex': 'Codex'}
MAX_OUTPUT = 4 * 1024 * 1024
_ACTIVE = {}
_ACTIVE_LOCK = threading.RLock()
_IS_STOPPING = threading.Event()


class CollectError(Exception):
    def __init__(self, code):
        self.code = code


def terminate_active_collectors():
    """Permanently stop new probes and reap all registered CLI process groups."""
    _IS_STOPPING.set()
    with _ACTIVE_LOCK:
        processes = list(_ACTIVE.values())
    for process in processes:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    for process in processes:
        process.wait()


def _cleanup(process):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()
    for stream in (process.stdin, process.stdout):
        if stream is not None:
            stream.close()


def _read_event(process, selector, state, deadline):
    while True:
        if b'\n' in state['buffer']:
            line, state['buffer'] = state['buffer'].split(b'\n', 1)
            if line.strip():
                return json.loads(line)
            continue
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise CollectError('timeout')
        if not selector.select(remaining):
            raise CollectError('timeout')
        chunk = os.read(process.stdout.fileno(), 65536)
        if not chunk:
            if state['buffer'].strip():
                line, state['buffer'] = state['buffer'], b''
                return json.loads(line)
            return None
        state['size'] += len(chunk)
        if state['size'] > MAX_OUTPUT:
            raise CollectError('parse_error')
        state['buffer'] += chunk


def _send(process, payload):
    try:
        process.stdin.write((json.dumps(payload) + '\n').encode())
        process.stdin.flush()
    except (BrokenPipeError, OSError) as error:
        raise CollectError('rpc_error') from error


def _rpc_response(process, selector, state, deadline, identifier):
    while True:
        event = _read_event(process, selector, state, deadline)
        if event is None:
            raise CollectError('rpc_error')
        if isinstance(event, dict) and event.get('id') == identifier:
            if 'error' in event or not isinstance(event.get('result'), dict):
                raise CollectError('rpc_error')
            return event['result']


def _codex(process, selector, state, deadline):
    _send(process, {'id': 1, 'method': 'initialize', 'params': {
        'clientInfo': {'name': 'wtf-usage', 'version': '1.0'},
        'capabilities': {'experimentalApi': True}}})
    _rpc_response(process, selector, state, deadline, 1)
    _send(process, {'method': 'initialized', 'params': {}})
    _send(process, {'id': 2, 'method': 'account/rateLimits/read', 'params': {}})
    payload = _rpc_response(process, selector, state, deadline, 2)
    return parse_codex(payload)


def _command(process, selector, state, deadline, provider):
    chunks = []
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not selector.select(remaining):
            raise CollectError('timeout')
        chunk = os.read(process.stdout.fileno(), 65536)
        if not chunk:
            break
        state['size'] += len(chunk)
        if state['size'] > MAX_OUTPUT:
            raise CollectError('parse_error')
        chunks.append(chunk)
    try:
        process.wait(timeout=max(0.001, deadline - time.monotonic()))
    except subprocess.TimeoutExpired as error:
        raise CollectError('timeout') from error
    if process.returncode != 0:
        raise CollectError('command_failed')
    raw = b''.join(chunks).decode('utf-8')
    return (parse_claude(raw) if provider == 'claude' else parse_agy(raw)), False


def _collect(provider):
    deadline = time.monotonic() + 44
    with _ACTIVE_LOCK:
        if _IS_STOPPING.is_set():
            raise CollectError('command_failed')
        process = subprocess.Popen(COMMANDS[provider], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   start_new_session=True)
        _ACTIVE[process.pid] = process
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            state = {'buffer': b'', 'size': 0}
            if provider == 'codex':
                return _codex(process, selector, state, deadline)
            process.stdin.close()
            return _command(process, selector, state, deadline, provider)
    finally:
        try:
            _cleanup(process)
        finally:
            with _ACTIVE_LOCK:
                _ACTIVE.pop(process.pid, None)


def collect_provider(provider):
    """Return a sanitized provider result, including explicit unknown failures."""
    if provider not in COMMANDS:
        raise ValueError('unknown provider')
    attempted = utc_now()
    result = dict(id=provider, label=LABELS[provider], status='error',
                  source='local_cli_rpc' if provider == 'codex' else 'local_cli',
                  observed_at=None, attempted_at=attempted, error_code=None,
                  buckets=[], usage_blocked=False)
    try:
        result['buckets'], result['usage_blocked'] = _collect(provider)
        result.update(status='ok', observed_at=utc_now())
    except FileNotFoundError:
        result['error_code'] = 'cli_missing'
    except CollectError as error:
        result['error_code'] = error.code
    except (ParseError, ValueError, TypeError, KeyError, AttributeError, UnicodeError):
        result['error_code'] = 'parse_error'
    except OSError:
        result['error_code'] = 'command_failed'
    return result
