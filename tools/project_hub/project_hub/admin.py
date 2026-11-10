"""Shared locked compatibility implementations for hub_admin and update_card."""
import argparse
import re
from .errors import HubError
from .registry import Registry, stable_id
from .report import sync_progress
from .state import now
from .storage import edit_status


def change_todos(data, command, args):
    todos = data.setdefault("todos", [])
    if command == "decide":
        identifier, text, *state = args
        item = next((row for row in todos if row["id"] == identifier), None)
        if item is None:
            raise HubError("todo_not_found", f"找不到 {identifier}", 404)
        item["decided"] = text
        if state:
            item["state"] = state[0]
    elif command == "remove":
        if set(args) - {row["id"] for row in todos}:
            raise HubError("todo_not_found", "有 id 找不到", 404)
        data["todos"] = [row for row in todos if row["id"] not in args]
    elif command == "doing":
        data["doing"] = args[0]
    elif command == "add":
        identifier, source, quote, todo, owner, *images = args
        todos.append(dict(id=identifier, at=now(), src=source, quote=quote, meet=None, todo=[todo], ask=None,
                          decided=None, imgs=images, photos=[], state="todo", origin=source,
                          note=f"負責線：{owner}", by="line", owner=owner))
    elif command == "owner":
        owner, identifiers = args[0], set(args[1:])
        for item in todos:
            if not identifiers or item["id"] in identifiers:
                item["owner"] = owner
                note, line = item.get("note") or "", f"負責線：{owner}（三藏指定）"
                item["note"] = re.sub(r"^(建議)?負責線：[^\n]*", line, note) if re.match(r"(建議)?負責線：", note) else line + ("\n" + note if note else "")
        data["line"] = "／".join(sorted({row["owner"] for row in todos if row.get("owner")}))
    else:
        raise HubError("invalid_command", "管理命令無效")


def main(argv=None, root=None, is_card=False):
    parser = argparse.ArgumentParser()
    parser.add_argument("args", nargs="+")
    args = parser.parse_args(argv).args
    project = Registry.make_project(dict(project_id=stable_id(str(root)), root=str(root)))
    command, exhibit, *rest = args if not is_card else ["card", *args]
    def update(data):
        if command == "card":
            identifier, *pairs = rest
            card = next((row for key in ("decisions", "reviews") for row in data.get(key, []) if row.get("id") == identifier), None)
            if card is None:
                raise HubError("card_not_found", "找不到卡片", 404)
            for pair in pairs:
                key, value = pair.split("=", 1)
                card[key] = None if value == "none" else value
            card["at"] = now()
        else:
            change_todos(data, command, rest)
        sync_progress(data)
        data["updated"] = now()
    edit_status(project, exhibit, update)
