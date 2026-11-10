#!/usr/bin/env python3
"""Legacy-compatible report CLI with explicit project root and shared storage lock."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "project_hub"
from .errors import HubError
from .paths import within
from .registry import Registry, stable_id
from .state import now
from .storage import edit_status, read_jsonl
from .cmux_adapter import CmuxAdapter
from .targets import Targets, IDENTITY


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--project-root", required=True)
    result.add_argument("--project-id")
    result.add_argument("cmd", choices=["set", "ask", "review", "page", "todo", "done", "inbox"])
    result.add_argument("exhibit")
    result.add_argument("item", nargs="?")
    for field in ("line", "doing", "light", "progress", "progress-label", "verify", "id", "q", "rec", "ref", "title", "before", "after", "page", "pages", "note", "state"):
        result.add_argument("--" + field)
    for field in ("file", "alert", "opt"):
        result.add_argument("--" + field, action="append", default=[])
    result.add_argument("--clear-alerts", action="store_true")
    return result


def surface():
    try:
        result = subprocess.run(["cmux", "identify", "--id-format", "both"], capture_output=True, text=True, timeout=5)
        caller = json.loads(result.stdout)["caller"]
        return {key: caller.get(key) for key in ("surface_id", "surface_ref", "workspace_id")}
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return None


def caller_target(project, caller):
    if not caller:
        return None
    def for_cwd(value):
        path = Path(value or "/").resolve()
        return project if path == project.root or project.root in path.parents else None
    registry = SimpleNamespace(for_cwd=for_cwd)
    targets = Targets(registry, CmuxAdapter()).list(project)["targets"]
    matches = [target for target in targets if target["can_bind"] and target["surface_id"] == caller.get("surface_id")
               and target["workspace_id"] == caller.get("workspace_id")]
    if len(matches) != 1:
        return None
    target = {key: matches[0][key] for key in (*IDENTITY, "line_id", "target_id", "name")}
    return dict(target, root=str(project.root), bound_at=now(), binding_version=1)


def file_info(project, relative):
    path = within(project.root, relative, public=True)
    if not path.is_file():
        return {"path": relative, "missing": True}
    stat, digest = path.stat(), hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return dict(path=relative, md5=digest.hexdigest(), size=stat.st_size, mtime=stat.st_mtime, at=now())


def sync_progress(data):
    todos = data.get("todos") or []
    if todos:
        data.setdefault("progress", {}).update(done=sum(row.get("state") == "done" for row in todos), total=len(todos))


def set_status(data, args, project):
    for field in ("line", "doing", "light"):
        if getattr(args, field) is not None:
            data[field] = getattr(args, field)
    if args.progress:
        done, total = args.progress.split("/")
        data.setdefault("progress", {}).update(done=int(done), total=int(total))
    if args.progress_label:
        data.setdefault("progress", {})["label"] = args.progress_label
    if args.verify:
        data.setdefault("verify", {}).update(dict(pair.split("=", 1) for pair in args.verify.split(",")))
    if args.file:
        files = {item["path"]: item for item in data.get("files", [])}
        files.update({relative: file_info(project, relative) for relative in args.file})
        data["files"] = list(files.values())
    if args.clear_alerts:
        data["alerts"] = []
    data.setdefault("alerts", []).extend(args.alert)


def add_card(data, args, project):
    if args.cmd == "page":
        data["pages"] = [row for row in data.get("pages", []) if row["path"] != args.page]
        data["pages"].append(dict(title=args.title, path=args.page, at=now()))
        return
    if not args.id:
        raise HubError("id_required", "請提供 --id")
    key = "decisions" if args.cmd == "ask" else "reviews"
    data[key] = [row for row in data.get(key, []) if row["id"] != args.id]
    if args.cmd == "ask":
        data[key].append(dict(id=args.id, q=args.q, options=args.opt, rec=int(args.rec) if args.rec is not None else -1, ref=args.ref, at=now()))
    else:
        data[key].append(dict(id=args.id, title=args.title, before=args.before, after=args.after,
                             page=args.page, pages=args.pages, note=args.note, at=now()))


def update_todo(data, args, project):
    row = next((row for row in data.get("todos", []) if row["id"] == args.item), None)
    if row is None:
        raise HubError("todo_not_found", f"找不到待辦 {args.item}", 404)
    state = args.state or row.get("state", "todo")
    if state == "done":
        print("已完成只能由 PO 驗收後設定，改記為 submitted（已提交）")
        state = "submitted"
    if state not in ("todo", "doing", "wait", "submitted"):
        raise HubError("invalid_state", "待辦狀態無效")
    row.update(state=state, by="line", at=now())
    if args.note is not None:
        row["note"] = args.note


def done(data, args, project):
    for field in ("decisions", "reviews"):
        data[field] = [row for row in data.get(field, []) if row["id"] != args.item]
    if args.note:
        timestamp = now()
        data.setdefault("answers", []).append(dict(uid=f"chat-{args.item}-{timestamp}", id=args.item,
            kind="chat", text=args.note, at=timestamp, delivery=dict(ok=True, at=timestamp)))


def inbox(data, args, project):
    rows = read_jsonl(within(project.data, f"inbox/{args.exhibit}.jsonl"))
    seen = set(data.get("read", []))
    fresh = [row for row in rows if row["uid"] not in seen]
    for row in fresh:
        print(json.dumps(row, ensure_ascii=False))
    data["read"] = sorted(seen | {row["uid"] for row in fresh})
    if not fresh:
        print("（沒有新的回覆）")


def main(argv=None):
    args = parser().parse_args(argv)
    project = Registry.make_project(dict(project_id=args.project_id or stable_id(Path(args.project_root).name), root=args.project_root))
    caller = surface() if args.cmd in ("set", "ask", "review", "page") else None
    target = caller_target(project, caller)
    handlers = dict(set=set_status, ask=add_card, review=add_card, page=add_card, todo=update_todo, done=done, inbox=inbox)
    def update(data):
        if caller:
            data["surface"] = caller
            if target:
                data["target"] = target
            else:
                print("目前工作線身分無法完整核對；保留既有綁定，需要時請在指揮中心連結。", file=sys.stderr)
        handlers[args.cmd](data, args, project)
        sync_progress(data)
        data["updated"] = now()
    edit_status(project, args.exhibit, update)


if __name__ == "__main__":
    try:
        main()
    except (HubError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
