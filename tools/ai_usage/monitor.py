"""Shared quota monitor and conservative dispatch checks."""
import argparse
import concurrent.futures
import contextlib
import copy
import datetime as dt
import json
import math
import signal
import sys
import threading
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.ai_usage import storage

PROVIDERS = ('claude', 'codex', 'agy')
SEVERITY = {'ok': 0, 'warning': 1, 'reserve': 2, 'exhausted': 3,
            'stale': 4, 'unknown': 5}
EXIT = {'ok': 0, 'warning': 1, 'reserve': 2, 'exhausted': 2,
        'stale': 3, 'unknown': 3}
STOPPING = threading.Event()


def terminate_collectors():
    STOPPING.set()
    from tools.ai_usage.collectors import terminate_active_collectors
    terminate_active_collectors()


@contextlib.contextmanager
def shutdown_signals(on_stop=None):
    def stop(signum, frame):
        if on_stop is not None:
            on_stop()
        terminate_collectors()
        raise KeyboardInterrupt
    previous = {number: signal.signal(number, stop)
                for number in (signal.SIGTERM, signal.SIGINT)}
    try:
        yield
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)


def bucket_state(bucket, observed_at, now):
    used = bucket.get('used_percent')
    remaining = bucket.get('remaining_percent')
    values = (used, remaining)
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(value) or not 0 <= value <= 100 for value in values):
        return 'unknown'
    if abs(used + remaining - 100) > 0.2:
        return 'unknown'
    observed = storage.epoch(observed_at)
    reset = storage.epoch(bucket.get('resets_at'))
    if observed is None or observed > now + 60:
        return 'unknown'
    if now - observed > 600 or (reset is not None and reset <= now):
        return 'stale'
    if bucket.get('resets_at') is not None and reset is None:
        return 'unknown'
    return ('exhausted' if used >= 100 else 'reserve' if used >= 95
            else 'warning' if used >= 80 else 'ok')


def compute(snapshot, now=None):
    now = dt.datetime.now(dt.timezone.utc).timestamp() if now is None else now
    result = copy.deepcopy(snapshot if is_snapshot(snapshot) else empty_snapshot())
    for provider in result.get('providers', []):
        for bucket in provider.get('buckets', []):
            bucket['state'] = bucket_state(bucket, provider.get('observed_at'), now)
        states = [bucket['state'] for bucket in provider.get('buckets', [])]
        if provider.get('status') != 'ok' or not states:
            states.append('unknown')
        if provider.get('usage_blocked'):
            states.append('exhausted')
        provider['state'] = max(states, key=SEVERITY.get)
        provider['exit_code'] = EXIT[provider['state']]
    return result


def is_snapshot(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get('schema_version') != 1:
        return False
    providers = snapshot.get('providers')
    if not isinstance(providers, list) or not providers:
        return False
    for provider in providers:
        if not isinstance(provider, dict) or provider.get('id') not in PROVIDERS:
            return False
        buckets = provider.get('buckets')
        if not isinstance(buckets, list) or any(not isinstance(item, dict) for item in buckets):
            return False
    return True


def empty_snapshot():
    return {'schema_version': 1, 'generated_at': None, 'providers': [
        {'id': key, 'label': key, 'status': 'error', 'source': None,
         'observed_at': None, 'attempted_at': None, 'error_code': 'not_collected',
         'usage_blocked': False, 'buckets': []} for key in PROVIDERS],
        'monitor': {'interval_seconds': 300, 'ttl_seconds': 600,
                    'heartbeat_at': None, 'started_at': None, 'refreshing': False}}


def status(runtime=storage.RUNTIME):
    snapshot = storage.read_json('snapshot.json', runtime) or empty_snapshot()
    metadata = storage.read_json('monitor.json', runtime)
    if metadata:
        snapshot['monitor'] = metadata
    return compute(snapshot)


def collect(provider):
    try:
        if STOPPING.is_set():
            raise RuntimeError('stopping')
        from tools.ai_usage.collectors import collect_provider
        return collect_provider(provider)
    except Exception:
        return {'id': provider, 'label': provider, 'status': 'error', 'source': None,
                'observed_at': None, 'attempted_at': storage.timestamp(),
                'error_code': 'collector_failed', 'buckets': []}


def refresh(runtime=storage.RUNTIME):
    try:
        with storage.lock('refresh.lock', runtime):
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                results = list(executor.map(lambda key: refresh_provider(key, runtime), PROVIDERS))
            if all(code == 429 for _, code in results):
                return {'error': 'cooldown'}, 429
            if any(code == 409 for _, code in results):
                return {'error': 'refresh_in_progress'}, 409
            return status(runtime), 200
    except BlockingIOError:
        return {'error': 'refresh_in_progress'}, 409


def refresh_provider(provider, runtime=storage.RUNTIME):
    if provider not in PROVIDERS or STOPPING.is_set():
        return {'error': 'unknown_provider' if provider not in PROVIDERS else 'stopping'}, 409
    try:
        with storage.lock(f'provider-{provider}.lock', runtime):
            previous = status(runtime)
            entry = next((item for item in previous['providers'] if item['id'] == provider), {})
            last = storage.epoch(entry.get('attempted_at'))
            if last is not None and dt.datetime.now(dt.timezone.utc).timestamp() - last < 60:
                return {'error': 'cooldown'}, 429
            entry = dict(collect(provider), id=provider)
            with storage.lock('update.lock', runtime, blocking=True):
                snapshot = status(runtime)
                snapshot['providers'] = [item for item in snapshot['providers'] if item['id'] != provider]
                snapshot['providers'].append(entry)
                snapshot['providers'].sort(key=lambda item: PROVIDERS.index(item['id']))
                snapshot['generated_at'] = storage.timestamp()
                snapshot = compute(snapshot)
                storage.persist(snapshot, runtime)
                return snapshot, 200
    except BlockingIOError:
        return {'error': 'refresh_in_progress'}, 409


def check(snapshot, provider_id, pool_id=None):
    provider = next((item for item in snapshot.get('providers', [])
                     if item['id'] == provider_id), None)
    scope = ('selected_pool_with_all_provider_guards' if pool_id
             else 'all_provider_pools_conservative')
    result = {'provider': provider_id, 'pool': pool_id, 'scope': scope,
              'scope_note': '指定池僅供聚焦；共享額度映射未完整驗證，一律以供應商所有池守門。額度不代表模型能力。'}
    if provider is None:
        return dict(result, state='unknown', exit_code=3, error='unknown_provider')
    buckets = provider.get('buckets', [])
    if pool_id:
        selected = [item for item in buckets if item.get('id') == pool_id]
        if not selected:
            return dict(result, state='unknown', exit_code=3, error='unknown_pool')
    states = [item['state'] for item in buckets] or ['unknown']
    if provider.get('status') != 'ok':
        states.append('unknown')
    if provider.get('usage_blocked'):
        states.append('exhausted')
    state = max(states, key=SEVERITY.get)
    return dict(result, state=state, exit_code=EXIT[state], buckets=buckets,
                usage_blocked=bool(provider.get('usage_blocked')))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('refresh')
    commands.add_parser('status')
    checker = commands.add_parser('check')
    checker.add_argument('--provider', required=True)
    checker.add_argument('--pool')
    serving = commands.add_parser('serve')
    serving.add_argument('--port', type=int, default=8766)
    args = parser.parse_args(argv)
    if args.command == 'serve':
        from tools.ai_usage.server import serve
        return serve(args.port)
    if args.command == 'refresh':
        try:
            with shutdown_signals():
                result, code = refresh()
            code = 0 if code == 200 else 3
        except KeyboardInterrupt:
            result, code = {'error': 'cancelled'}, 130
    elif args.command == 'check':
        result = check(status(), args.provider, args.pool)
        code = result['exit_code']
    else:
        result, code = status(), 0
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
