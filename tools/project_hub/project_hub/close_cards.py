"""Close selected decision/review cards under the shared project lock."""
import argparse
from .errors import HubError
from .registry import Registry, stable_id
from .state import now
from .storage import edit_status


def main(argv=None, root=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exhibit")
    parser.add_argument("note")
    parser.add_argument("ids", nargs="*")
    args = parser.parse_args(argv)
    project = Registry.make_project(dict(project_id=stable_id(str(root)), root=str(root)))
    def update(data):
        cards = data.get("decisions", []) + data.get("reviews", [])
        available = {card["id"] for card in cards}
        targets = available if args.ids == ["all"] else set(args.ids)
        if targets - available:
            raise HubError("card_not_found", f"找不到 {sorted(targets - available)}", 404)
        timestamp = now()
        for group in ("decisions", "reviews"):
            data[group] = [card for card in data.get(group, []) if card["id"] not in targets]
        for identifier in sorted(targets):
            data.setdefault("answers", []).append(dict(uid=f"chat-{identifier}-{timestamp}", id=identifier,
                kind="chat", text=args.note, at=timestamp, delivery=dict(ok=True, at=timestamp)))
        data["updated"] = timestamp
        print(args.exhibit, "關閉", len(targets), "剩", [card["id"] for card in data["decisions"] + data["reviews"]])
    edit_status(project, args.exhibit, update)
