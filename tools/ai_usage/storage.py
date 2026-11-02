"""Bounded, atomic local persistence. No account credentials are persisted."""
import contextlib
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'workingfiles/outputs/_shared/ai-usage-20261019/runtime'


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def epoch(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.timestamp() if parsed.tzinfo else None
    except (ValueError, OverflowError):
        return None


@contextlib.contextmanager
def lock(name, runtime=RUNTIME, blocking=False):
    runtime.mkdir(parents=True, exist_ok=True)
    with (runtime / name).open('a') as handle:
        flags = fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)
        fcntl.flock(handle, flags)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def atomic_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.usage-')
    try:
        with os.fdopen(descriptor, 'w') as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_json(name, runtime=RUNTIME):
    try:
        value = json.loads((runtime / name).read_text())
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def save_json(name, value, runtime=RUNTIME):
    atomic_write(runtime / name, json.dumps(value, ensure_ascii=False, allow_nan=False))


def read_history(runtime=RUNTIME):
    try:
        lines = (runtime / 'history.jsonl').read_text().splitlines()
    except OSError:
        return []
    cutoff = dt.datetime.now(dt.timezone.utc).timestamp() - 7 * 86400
    entries = []
    for line in lines[-10080:]:
        try:
            entry = json.loads(line)
            observed = epoch(entry.get('generated_at'))
            if observed is not None and observed >= cutoff:
                entries.append(entry)
        except (ValueError, AttributeError):
            continue
    return entries


def persist(snapshot, runtime=RUNTIME):
    with lock('write.lock', runtime, blocking=True):
        entries = read_history(runtime)
        entries.append(snapshot)
        payload = ''.join(json.dumps(item, ensure_ascii=False, allow_nan=False) + '\n'
                          for item in entries[-10080:])
        atomic_write(runtime / 'history.jsonl', payload)
        save_json('snapshot.json', snapshot, runtime)


def heartbeat(started_at, is_refreshing, runtime=RUNTIME):
    save_json('monitor.json', {'interval_seconds': 300, 'ttl_seconds': 600,
                             'heartbeat_at': timestamp(), 'started_at': started_at,
                             'refreshing': is_refreshing, 'running': True}, runtime)
