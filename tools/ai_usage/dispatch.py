"""Run one explicitly selected provider only after a conservative quota check."""
import argparse
import json
import os
import re
import signal
import subprocess
import sys
import uuid
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.ai_usage import monitor, storage

MAX_RECORDS = 1000
_is_cancelled = False


def _handle_termination(signum, frame):
    global _is_cancelled
    if _is_cancelled:
        return
    _is_cancelled = True
    from tools.ai_usage.collectors import terminate_active_collectors
    terminate_active_collectors()
    raise KeyboardInterrupt


def command(provider, model, prompt):
    if provider == 'claude':
        return ['claude', '-p', '--model', model, '--', prompt]
    if provider == 'agy':
        return ['agy', '--model', model, '--print', prompt, '--print-timeout', '600s']
    return ['codex', 'exec', '--model', model, '--', prompt]


def refresh_state(runtime, provider):
    try:
        _, code = monitor.refresh_provider(provider, runtime)
        return {200: 'updated', 429: 'cooldown', 409: 'in_progress'}.get(code, 'failed')
    except (OSError, ValueError):
        return 'failed'


def check_summary(result):
    return {key: result.get(key) for key in
            ('provider', 'pool', 'scope', 'state', 'exit_code', 'usage_blocked')}


def clear_observed_dirty(provider, runtime, snapshot, check_started):
    name = f'dispatch-{provider}-dirty.json'
    marker = storage.read_json(name, runtime)
    if not marker:
        return True
    threshold = storage.epoch(marker.get('ended_at') or check_started)
    item = next((item for item in snapshot.get('providers', []) if item['id'] == provider), {})
    attempted = storage.epoch(item.get('attempted_at'))
    observed = storage.epoch(item.get('observed_at'))
    if (item.get('status') != 'ok' or threshold is None or attempted is None
            or observed is None or attempted < threshold or observed < attempted):
        return False
    (runtime / name).unlink(missing_ok=True)
    return True


def run_marked(provider, model, prompt, runtime, record):
    name = f'dispatch-{provider}-dirty.json'
    storage.save_json(name, {'started_at': storage.timestamp(), 'ended_at': None}, runtime)
    try:
        record['exit_code'], record['status'] = execute(command(provider, model, prompt))
        return record['exit_code']
    finally:
        record['ended_at'] = storage.timestamp()
        storage.save_json(name, {'ended_at': record['ended_at']}, runtime)


def save_record(record, runtime):
    with storage.lock('dispatch.lock', runtime, blocking=True):
        path = runtime / 'dispatch.jsonl'
        try:
            # Bounded reads even if an unrelated process replaced this file.
            with path.open('rb') as handle:
                handle.seek(0, os.SEEK_END)
                handle.seek(max(0, handle.tell() - 2 * 1024 * 1024))
                lines = handle.read().decode('utf-8', errors='ignore').splitlines()
        except FileNotFoundError:
            lines = []
        entries = []
        for line in lines[-MAX_RECORDS + 1:]:
            try:
                entry = json.loads(line)
                if isinstance(entry, dict):
                    entries.append({key: entry[key] for key in record if key in entry})
            except ValueError:
                continue
        entries.append(record)
        storage.atomic_write(path, ''.join(json.dumps(item, ensure_ascii=False) + '\n'
                                           for item in entries[-MAX_RECORDS:]))


def execute(arguments):
    process = None
    try:
        process = subprocess.Popen(arguments, stdin=subprocess.DEVNULL, start_new_session=True)
        return process.wait(timeout=600), 'finished'
    except FileNotFoundError:
        return 127, 'cli_missing'
    except subprocess.TimeoutExpired:
        return 124, 'timeout'
    except KeyboardInterrupt:
        return 130, 'interrupted'
    except OSError:
        return 126, 'command_failed'
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def _dispatch_locked(provider, model, prompt, pool, allow_warning, runtime):
    record = dict(task_id=uuid.uuid4().hex, provider=provider, model=model,
                  started_at=storage.timestamp(), ended_at=None, status='blocked',
                  exit_code=3, before_refresh=None, after_refresh=None, check=None)
    try:
        check_started = storage.timestamp()
        record['before_refresh'] = refresh_state(runtime, provider)
        if record['before_refresh'] in ('failed', 'in_progress'):
            print('額度刷新失敗或正在採集，暫停派工。', file=sys.stderr)
            return 3
        snapshot = monitor.status(runtime)
        if not clear_observed_dirty(provider, runtime, snapshot, check_started):
            print('前次派工後尚無新額度觀測，暫停派工。', file=sys.stderr)
            return 3
        result = monitor.check(snapshot, provider, pool)
        record['check'] = check_summary(result)
        code = result['exit_code']
        if code not in (0, 1) or (code == 1 and not allow_warning):
            record['exit_code'] = code
            print(json.dumps(record['check'], ensure_ascii=False), file=sys.stderr)
            return code
        return run_marked(provider, model, prompt, runtime, record)
    finally:
        record['after_refresh'] = 'cancelled' if _is_cancelled else refresh_state(runtime, provider)
        record['ended_at'] = record['ended_at'] or storage.timestamp()
        if not _is_cancelled:
            clear_observed_dirty(provider, runtime, monitor.status(runtime), record['ended_at'])
        if record['after_refresh'] != 'updated':
            print('派工後額度尚未更新：' + record['after_refresh'], file=sys.stderr)
        try:
            save_record(record, runtime)
        except OSError:
            print('派工紀錄無法寫入。', file=sys.stderr)


def dispatch(provider, model, prompt, pool=None, allow_warning=False, runtime=storage.RUNTIME):
    if provider not in monitor.PROVIDERS:
        raise ValueError('unknown provider')
    try:
        with storage.lock(f'dispatch-{provider}.lock', runtime):
            return _dispatch_locked(provider, model, prompt, pool, allow_warning, runtime)
    except BlockingIOError:
        print('此供應商已有派工執行中，暫停派工。', file=sys.stderr)
        return 3
    except OSError:
        print('額度守門狀態無法安全讀寫，暫停派工。', file=sys.stderr)
        return 3


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=monitor.PROVIDERS, required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--prompt-file', type=Path, required=True)
    parser.add_argument('--pool')
    parser.add_argument('--allow-warning', action='store_true')
    args = parser.parse_args(argv)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}', args.model):
        parser.error('model 必須是模型識別名稱')
    try:
        prompt = args.prompt_file.read_text(encoding='utf-8')
    except (OSError, UnicodeError):
        parser.error('無法讀取 UTF-8 prompt 檔案')
    if not prompt.strip():
        parser.error('prompt 檔案不得為空')
    previous = signal.signal(signal.SIGTERM, _handle_termination)
    try:
        return dispatch(args.provider, args.model, prompt, args.pool, args.allow_warning)
    except KeyboardInterrupt:
        return 130
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == '__main__':
    raise SystemExit(main())
