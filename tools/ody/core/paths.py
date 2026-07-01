"""路徑錨點。所有相對路徑一律以 framework 根 / WTF repo 根 為基準解析，禁裸相對路徑。"""
from __future__ import annotations
from pathlib import Path

# tools/assistant/core/paths.py -> tools/assistant
ASSISTANT_ROOT = Path(__file__).resolve().parent.parent
# WTF repo 根（tools/assistant -> tools -> repo）
WTF_ROOT = ASSISTANT_ROOT.parent.parent

DATA_DIR = ASSISTANT_ROOT / "data"
OUTPUTS_DIR = ASSISTANT_ROOT / "outputs"
SCHEMAS_DIR = ASSISTANT_ROOT / "schemas"
TASKS_DIR = ASSISTANT_ROOT / "tasks"
EVENTS_PATH = DATA_DIR / "events.jsonl"
DRAFTS_DIR = DATA_DIR / "drafts"


def ensure_dirs() -> None:
    for d in (DATA_DIR, OUTPUTS_DIR, DRAFTS_DIR):
        d.mkdir(parents=True, exist_ok=True)
