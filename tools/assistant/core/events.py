"""結構化事件記錄 — events.jsonl 每行一筆，schema 驗證後才落地。

這是學習迴圈與成本指標的唯一資料來源（單一真相源）。
"""
from __future__ import annotations
import json
from datetime import datetime, timezone

from . import validate
from .paths import EVENTS_PATH, SCHEMAS_DIR, ensure_dirs

_SCHEMA = json.loads((SCHEMAS_DIR / "event.schema.json").read_text(encoding="utf-8"))


class EventLog:
    def __init__(self, task_id: str, run_id: str):
        self.task_id = task_id
        self.run_id = run_id
        ensure_dirs()

    def emit(self, phase: str, **fields) -> dict:
        ev = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "task_id": self.task_id,
            "run_id": self.run_id,
            "phase": phase,
        }
        # 過濾 None：稀疏事件，不記空欄（避免 null 違反 schema 型別）
        ev.update({k: v for k, v in fields.items() if v is not None})
        validate.validate(ev, _SCHEMA)  # 不合即 raise，壞事件不入庫
        with EVENTS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ev


def read_all() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    out = []
    for line in EVENTS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out
