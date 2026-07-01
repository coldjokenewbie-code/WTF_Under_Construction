"""AI 中立 Adapter — 把「呼叫某個 LLM」抽象成統一介面，底層可換 claude / codex / agy。

設計重點：
- 各 AI 只是可替換的「行為引擎」，框架不綁定任一家。
- 預設 dry-run：不真的花 API（呼應「省」與「可離線驗收」）；--allow-llm 才真呼叫。
- 真呼叫一律走受控 executor + Policy Gate（LLM 不直接碰檔案/網路）。
- Fallback Payload 協議：把 handler 執行軌跡與失敗原因打包進 prompt，避免 LLM 重做已完成步驟。
"""
from __future__ import annotations
import json
from dataclasses import dataclass

from . import executor

# 後端 → headless argv 樣板（{prompt} 由呼叫端填）
BACKENDS = {
    "claude": lambda p: ["claude", "-p", p],
    "codex": lambda p: ["codex", "exec", p, "-s", "read-only", "--skip-git-repo-check"],
    "agy": lambda p: ["agy", "-p", p],
}


@dataclass
class FallbackPayload:
    """退回 LLM 時統一傳遞的脈絡（避免狀態丟失/重做）。"""
    goal: str
    context: str
    handler_trace: dict
    failure_reason: str
    constraints: dict

    def to_prompt(self) -> str:
        return (
            "請用繁體中文台灣用語協助修復一個自動任務。只輸出修復建議，不要讀寫檔。\n"
            f"目標：{self.goal}\n"
            f"脈絡：{self.context}\n"
            f"已執行軌跡（勿重做已成功步驟）：{json.dumps(self.handler_trace, ensure_ascii=False)}\n"
            f"失敗原因：{self.failure_reason}\n"
            f"限制：{json.dumps(self.constraints, ensure_ascii=False)}\n"
        )


@dataclass
class AdapterResult:
    backend: str
    called: bool          # 是否真的花了 API
    planned_argv: list[str]
    output: str = ""
    note: str = ""


def call(payload: FallbackPayload, *, backend: str = "claude",
         dry_run: bool = True, timeout: int = 180) -> AdapterResult:
    if backend not in BACKENDS:
        raise ValueError(f"未知 backend：{backend}（可選 {list(BACKENDS)}）")
    argv = BACKENDS[backend](payload.to_prompt())
    if dry_run:
        return AdapterResult(backend, called=False, planned_argv=argv,
                             note="dry-run：未呼叫 LLM、未花 API（預設省成本）")
    res = executor.run(argv, allow_network=True, timeout=timeout)  # LLM CLI 需連線
    return AdapterResult(backend, called=True, planned_argv=argv,
                         output=(res.stdout or res.stderr or res.blocked_reason or ""),
                         note=("ok" if res.ok else "fallback 呼叫失敗"))
