"""Process-safe read/modify/write over legacy JSON and JSONL."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import tempfile
import threading
from .errors import HubError
from .paths import exhibit_name, name_key, no_symlinks, within

_GUARD = threading.Lock()
_LOCKS = {}


def read_json(path, default=None):
    path = no_symlinks(path)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as error:
        raise HubError("invalid_data", f"資料無法讀取：{path.name}", 422) from error


def read_jsonl(path):
    path = no_symlinks(path)
    if not path.exists():
        return []
    try:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if any(not isinstance(row, dict) for row in rows):
            raise ValueError("record is not an object")
        return rows
    except (ValueError, OSError) as error:
        raise HubError("invalid_data", f"紀錄無法讀取：{path.name}", 422) from error


def atomic_json(path, value):
    path = no_symlinks(path)
    no_symlinks(path.parent).mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".hub-")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=1)
            stream.flush()
            os.fsync(stream.fileno())
        no_symlinks(path)
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def append_jsonl(path, value):
    path = no_symlinks(path)
    no_symlinks(path.parent).mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def locked(directory):
    directory = no_symlinks(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with _GUARD:
        mutex = _LOCKS.setdefault(str(directory), threading.RLock())
    with mutex:
        path = no_symlinks(directory / ".hub.lock")
        with path.open("a") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)


def status_path(data, exhibit):
    exhibit_name(exhibit)
    directory = within(data, "status")
    if directory.exists():
        collisions = [path for path in directory.glob("*.json") if name_key(path.stem) == name_key(exhibit)]
        if len(collisions) > 1 or (collisions and collisions[0].stem != exhibit):
            raise HubError("name_collision", "工作項目名稱與現有檔案正規化後重複", 409)
    return within(data, f"status/{exhibit}.json")


def edit_status(project, exhibit, update):
    with locked(project.data):
        path = status_path(project.data, exhibit)
        value = read_json(path, {"exhibit": exhibit, "decisions": [], "reviews": [], "files": [], "alerts": []})
        if not isinstance(value, dict):
            raise HubError("invalid_data", "工作項目資料必須是物件", 422)
        result = update(value)
        atomic_json(path, value)
        return result
