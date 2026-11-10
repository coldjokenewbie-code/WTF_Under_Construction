"""Durable routing with explicit uncertainty; no exactly-once claim."""
import datetime as dt
import time
import uuid
import shlex
from pathlib import Path
import subprocess
from .errors import HubError
from .paths import exhibit_name, within
from .state import now
from .storage import append_jsonl, locked, read_json, read_jsonl, status_path

RETRY_EVERY = 30
RETRY_MAX = 3600


def latest(project, uid):
    return next((row for row in reversed(read_jsonl(within(project.data, "deliveries.jsonl"))) if row.get("uid") == uid), None)


def record(project, row, state, **fields):
    result = dict(uid=row["uid"], state=state, ok=state in ("queued", "delivered", "read"), at=now(), attempts=0,
                  err="", retrying=False, target=row.get("target"), first_at=row["at"])
    result.update(fields)
    append_jsonl(within(project.data, "deliveries.jsonl"), result)
    return result


def build_message(row):
    text = f"【指揮中心】{row['exhibit']} {row['id']} "
    if row["kind"] == "note":
        return text + "指示：" + row["text"]
    label = "審閱" if row["kind"] == "review" else "裁決"
    text += f"{label}：{row.get('choice') or '（未選）'}"
    if row.get("text"):
        text += "；補充：" + row["text"]
    if row.get("title"):
        text += "；題目：" + row["title"]
    command = ["python3", str(Path(__file__).with_name("report.py")), "--project-root",
               row["root"], "--project-id", row["project_id"], "done", row["exhibit"], row["id"]]
    return text + "。處理完請執行 " + shlex.join(command)


class Router:
    def __init__(self, registry, targets, adapter, mode="disabled"):
        if mode not in ("disabled", "enabled"):
            raise HubError("invalid_mode", "傳送模式無效")
        self.registry, self.targets, self.adapter, self.mode = registry, targets, adapter, mode

    def answer(self, project, payload):
        exhibit = exhibit_name(payload["exhibit"])
        row = dict(uid=uuid.uuid4().hex, exhibit=exhibit, id=payload["id"], kind=payload.get("kind", "decision"),
                   choice=payload.get("choice", ""), text=payload.get("text", "").strip(), at=now(),
                   project_id=project.project_id, root=str(project.root))
        if row["kind"] not in ("decision", "review", "note") or not (row["choice"] or row["text"]):
            raise HubError("invalid_answer", "請提供選項或補充文字")
        with locked(project.data):
            status = read_json(status_path(project.data, exhibit), {})
            if not status:
                raise HubError("exhibit_not_found", "找不到工作項目", 404)
            row["target"] = status.get("target")
            card = next((card for group in ("decisions", "reviews") for card in status.get(group, []) if card.get("id") == row["id"]), {})
            row["title"] = card.get("q") or card.get("title") or ""
            append_jsonl(within(project.data, f"inbox/{exhibit}.jsonl"), row)
        return {"ok": True, "uid": row["uid"], "delivery": self.deliver(project, row)}

    def deliver(self, project, row):
        with locked(project.data):
            previous = latest(project, row["uid"])
            if previous and previous.get("state") in ("queued", "delivered", "read", "uncertain", "awaiting_binding", "gave_up", "disabled", "retargeted"):
                return previous
            if self.mode == "disabled":
                return record(project, row, "disabled", err="候選服務禁用傳送")
            if previous and previous.get("state") == "sending":
                return record(project, row, "uncertain", err="上次程序中斷；需人工確認外部收件狀態")
            validation = self.targets.validate_snapshot(project, row.get("target"))
            if validation is None:
                return record(project, row, "failed", err="工作線身分服務暫時不可用；尚未外送", safe_retry=True, retrying=True,
                              attempts=(previous or {}).get("attempts", 0))
            if not validation:
                return record(project, row, "awaiting_binding", err="原工作線失效或未連結；回覆保留在 inbox")
            attempts = (previous or {}).get("attempts", 0) + 1
            record(project, row, "sending", attempts=attempts)
            result = self.adapter.send(row["target"], build_message(row))
            state = result.get("state")
            if state not in ("queued", "failed", "uncertain"):
                state = "uncertain"
            is_safe = state == "failed" and result.get("safe_retry") is True
            return record(project, row, state, attempts=attempts, err=result.get("err", ""),
                          receipt_id=result.get("receipt_id"), retrying=is_safe, safe_retry=is_safe)

    def resend(self, project, exhibit, uid, rebind=False):
        if self.mode == "disabled":
            raise HubError("delivery_disabled", "候選服務禁止重送", 403)
        rows = read_jsonl(within(project.data, f"inbox/{exhibit_name(exhibit)}.jsonl"))
        row = next((row for row in rows if row.get("uid") == uid), None)
        previous = latest(project, uid) or {}
        if row is None:
            raise HubError("answer_not_found", "找不到回覆", 404)
        if rebind:
            return self.retarget(project, row, previous)
        if previous.get("state") != "failed" or not previous.get("safe_retry"):
            raise HubError("manual_review_required", "此回覆不能安全重送；請先人工核對收件狀態", 409)
        return {"ok": True, "delivery": self.deliver(project, row)}

    def retarget(self, project, row, previous):
        if previous.get("state") not in ("awaiting_binding", "retargeted"):
            raise HubError("manual_review_required", "只有確定尚未投遞的待綁回覆可明確改投", 409)
        with locked(project.data):
            status = read_json(status_path(project.data, row["exhibit"]), {})
            target = status.get("target")
            if not self.targets.validate_snapshot(project, target):
                raise HubError("target_unverified", "請先明確連結目前工作線", 409)
            path = within(project.data, f"inbox/{row['exhibit']}.jsonl")
            replacement = next((item for item in read_jsonl(path) if item.get("supersedes") == row["uid"]), None)
            if replacement is None:
                replacement = dict(row, uid=uuid.uuid4().hex, at=now(), target=target, supersedes=row["uid"],
                                   root=str(project.root), project_id=project.project_id)
                append_jsonl(path, replacement)
            record(project, row, "retargeted", replacement_uid=replacement["uid"])
        return {"ok": True, "uid": replacement["uid"], "delivery": self.deliver(project, replacement)}

    def recover(self):
        if self.mode == "disabled":
            return
        for project in self.registry.projects:
            try:
                self.recover_project(project)
            except (HubError, OSError, KeyError, TypeError):
                continue

    def recover_project(self, project):
        with locked(project.data):
            last = {row["uid"]: row for row in read_jsonl(within(project.data, "deliveries.jsonl"))}
            for path in within(project.data, "inbox").glob("*.jsonl"):
                for row in read_jsonl(path):
                    previous = last.get(row["uid"], {})
                    if previous.get("state") == "sending":
                        record(project, row, "uncertain", err="服務中斷時外部傳送結果不確定，請人工處理")
                    elif not row.get("target") and previous.get("retrying"):
                        record(project, row, "awaiting_binding", err="舊回覆未保存收件身分，不自動轉送")
                    elif not previous:
                        record(project, row, "failed" if row.get("target") else "awaiting_binding",
                               err="已保存回覆，尚未嘗試傳送", safe_retry=bool(row.get("target")), retrying=bool(row.get("target")))

    def retry_tick(self, timestamp=None):
        if self.mode == "disabled":
            return
        for project in self.registry.projects:
            try:
                self.retry_project(project, time.time() if timestamp is None else timestamp)
            except (HubError, OSError, KeyError, TypeError, ValueError):
                continue

    def retry_project(self, project, timestamp):
        for path in within(project.data, "inbox").glob("*.jsonl"):
            for row in read_jsonl(path):
                previous = latest(project, row["uid"]) or {}
                if previous.get("state") in ("queued", "delivered") and row.get("target"):
                    self.track_receipt(project, row, previous)
                if previous.get("state") != "failed" or not previous.get("safe_retry"):
                    continue
                first = dt.datetime.fromisoformat(row["at"]).timestamp()
                attempted = dt.datetime.fromisoformat(previous["at"]).timestamp()
                if timestamp - first > RETRY_MAX:
                    with locked(project.data):
                        record(project, row, "gave_up", err=previous.get("err", ""), attempts=previous.get("attempts", 0))
                elif timestamp - attempted >= RETRY_EVERY:
                    self.deliver(project, row)

    def track_receipt(self, project, row, previous):
        try:
            receipt = self.adapter.receipt(row["target"], previous.get("receipt_id"))
        except (OSError, ValueError, KeyError, subprocess.SubprocessError):
            return
        if not receipt:
            return
        state = "read" if receipt.get("read_at") else "delivered" if receipt.get("delivered_at") else "queued"
        if receipt.get("state") == "failed" and not receipt.get("delivered_at"):
            state = "uncertain"
        if state != previous.get("state"):
            with locked(project.data):
                record(project, row, state, receipt_id=previous.get("receipt_id"), attempts=previous.get("attempts", 0),
                       delivered_at=receipt.get("delivered_at"), read_at=receipt.get("read_at"), err=receipt.get("failure_reason") or "")
