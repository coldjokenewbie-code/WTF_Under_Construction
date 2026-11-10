"""Read legacy project state without changing any project data."""
import datetime as dt
import hashlib
import subprocess
import time
from pathlib import Path
from .errors import HubError
from .paths import no_symlinks, within
from .storage import read_json, read_jsonl

_HASHES = {}
_OPEN = {"at": 0, "paths": set()}


def open_office_files():
    if time.time() - _OPEN["at"] > 15:
        try:
            result = subprocess.run(["lsof", "-Fn", "-c", "Microsoft"], capture_output=True, text=True, timeout=5)
            _OPEN["paths"] = {line[1:] for line in result.stdout.splitlines() if line.startswith("n/")}
        except (OSError, subprocess.SubprocessError):
            _OPEN["paths"] = set()
        _OPEN["at"] = time.time()
    return _OPEN["paths"]


def now():
    return dt.datetime.now().isoformat(timespec="seconds")


def current_hash(path):
    stat = path.stat()
    key = (str(path), stat.st_mtime_ns, stat.st_size)
    if key not in _HASHES:
        digest = hashlib.md5()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        _HASHES[key] = digest.hexdigest()
    return _HASHES[key]


def update_files(project, exhibit):
    warnings = list(exhibit.get("alerts") or [])
    files = []
    for value in exhibit.get("files") or []:
        item = {"path": value} if isinstance(value, str) else value
        if not isinstance(item, dict):
            warnings.append("忽略無法識別的 files 項目")
            continue
        files.append(item)
        try:
            path = within(project.root, item["path"], public=True)
            item["open"] = str(path) in open_office_files()
            if not path.is_file():
                item["state"] = "missing"
                warnings.append(f"檔案不見：{path.name}")
                continue
            stat = path.stat()
            changed = item.get("size") is not None and (stat.st_size != item["size"] or abs(stat.st_mtime - item.get("mtime", 0)) > 1)
            if changed:
                item["state"] = "changed"
                item["current_md5"] = current_hash(path)
                if not path.name.startswith("W_"):
                    warnings.append(f"回報後又被改過：{path.name}")
        except (HubError, OSError, KeyError, TypeError) as error:
            item["state"] = "invalid"
            warnings.append(f"檔案路徑無法檢查：{error}")
    exhibit["files"] = files
    exhibit["warnings"] = warnings


def read_exhibit(project, path, deliveries):
    exhibit = read_json(path)
    if not isinstance(exhibit, dict) or not isinstance(exhibit.get("exhibit"), str):
        raise HubError("invalid_data", f"工作項目格式無效：{path.name}", 422)
    if exhibit["exhibit"] != path.stem:
        raise HubError("exhibit_filename_mismatch", f"exhibit須與檔名一致：{path.stem}", 422)
    update_files(project, exhibit)
    todos = exhibit.get("todos") or []
    if todos:
        exhibit.setdefault("progress", {}).update(done=sum(item.get("state") == "done" for item in todos), total=len(todos))
    answers = read_jsonl(within(project.data, f"inbox/{path.stem}.jsonl"))
    for answer in answers:
        answer["delivery"] = deliveries.get(answer.get("uid"))
        if answer["delivery"]:
            answer["delivery"] = dict(answer["delivery"], can_rebind=answer["delivery"].get("state") == "awaiting_binding" and bool(exhibit.get("target")))
    exhibit["answers"] = answers + [row for row in exhibit.get("answers", []) if row.get("kind") == "chat"]
    try:
        updated = dt.datetime.fromisoformat(exhibit["updated"])
        exhibit["age_min"] = (dt.datetime.now(updated.tzinfo) - updated).total_seconds() / 60
    except (KeyError, ValueError, TypeError):
        exhibit["age_min"] = None
    return exhibit


def project_state(project):
    result = dict(project_id=project.project_id, id=project.project_id, name=project.name,
                  deadline=None, deadline_label=None, pages=[], exhibits=[], diagnostics=[])
    if not project.root.is_dir():
        result["diagnostics"].append("專案工作目錄暫時離線")
        return result
    try:
        config = read_json(within(project.data, "config.json"), {})
        if not isinstance(config, dict):
            raise HubError("invalid_data", "config.json 必須是物件", 422)
        result.update({key: config.get(key) for key in ("deadline", "deadline_label")})
        result["pages"] = config.get("pages") or []
        latest = {row["uid"]: row for row in read_jsonl(within(project.data, "deliveries.jsonl"))}
    except (HubError, OSError, KeyError, TypeError) as error:
        result["diagnostics"].append(str(error))
        config, latest = {}, {}
    order = config.get("exhibits") or []
    try:
        directory = within(project.data, "status")
        paths = sorted(directory.glob("*.json"), key=lambda path: (order.index(path.stem) if path.stem in order else 999, path.stem))
        for path in paths:
            try:
                result["exhibits"].append(read_exhibit(project, path, latest))
            except (HubError, OSError, TypeError, KeyError, ValueError) as error:
                result["diagnostics"].append(f"{path.name}：{error}")
    except (HubError, OSError) as error:
        result["diagnostics"].append(str(error))
    return result


def snapshot(registry, delivery_mode):
    return {"projects": [project_state(project) for project in registry.projects], "now": now(), "delivery_mode": delivery_mode}
