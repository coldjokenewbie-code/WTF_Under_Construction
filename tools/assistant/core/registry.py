"""Tool/Skill Registry — task_type → 確定性 handler 的本地優先路由表。

每個項目帶 version + I/O 契約（input_params / outputs），利於回滾與學習追溯。
這是「本地優先」的關鍵：命中 registry 就跑確定性 handler、完全繞過 LLM。
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from typing import Callable

from ..handlers import project_digest, config_sync_check, kiosk_build_verify
from .paths import ASSISTANT_ROOT


@dataclass
class Entry:
    task_type: str
    handler: Callable          # (spec, ctx) -> HandlerResult
    version: str
    summary: str
    input_params: dict = field(default_factory=dict)   # 參數名 -> 說明
    outputs: list[str] = field(default_factory=list)   # 產物描述
    uses_llm: bool = False     # 確定性 handler 一律 False
    # 授權前置評估用的能力宣告（預設全 False＝只讀+寫沙盒，不需任何授權）
    capabilities: dict = field(default_factory=dict)   # paid_api/live_site/install/network/writes_user_files/destructive


REGISTRY: dict[str, Entry] = {
    "project_digest": Entry(
        task_type="project_digest",
        handler=project_digest.run,
        version="1.0.0",
        summary="掃 projects-registry 本機各 repo 唯讀 git log，彙整成 HTML 動態摘要（零 LLM）",
        input_params={"since": "git log --since（如 '7 days ago'）", "limit": "每 repo 取幾筆"},
        outputs=["outputs/project-digest_*.html"],
        uses_llm=False,
    ),
    "config_sync_check": Entry(
        task_type="config_sync_check",
        handler=config_sync_check.run,
        version="1.0.0",
        summary="跑 sync_config.py check（唯讀）回報跨工具設定是否與 SSOT 一致（零 LLM）",
        input_params={},
        outputs=["outputs/config-sync_*.txt"],
        uses_llm=False,
    ),
    "kiosk_build_verify": Entry(
        task_type="kiosk_build_verify",
        handler=kiosk_build_verify.run,
        version="1.0.0",
        summary="headless 載入 HTML 頁面截圖 + 對 visual_assertions 逐項機檢（斷圖/console/溢出/字數/置中），零 LLM、只渲染本地檔不操作活站",
        input_params={"page": "HTML 路徑", "viewport": "{w,h}", "settle_ms": "進場動畫等待",
                      "visual_assertions": "斷言清單（見 schema/tasks 範例）"},
        outputs=["outputs/kiosk-verify_*/shot.png", "outputs/kiosk-verify_*/report.html"],
        uses_llm=False,
    ),
}


def lookup(task_type: str) -> Entry | None:
    return REGISTRY.get(task_type)


def to_contract() -> dict:
    out = {}
    for k, e in REGISTRY.items():
        d = asdict(e)
        d.pop("handler")  # callable 不可序列化
        out[k] = d
    return out


def dump_contract() -> str:
    path = ASSISTANT_ROOT / "registry.json"
    path.write_text(json.dumps(to_contract(), ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
