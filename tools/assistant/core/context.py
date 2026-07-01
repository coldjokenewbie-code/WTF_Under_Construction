"""Handler 執行脈絡與結果型別。

handler 只透過 ctx 提供的受控介面動作（跑命令 / 寫產物），
不直接呼叫 subprocess、不自己決定寫哪裡 —— 安全邊界統一收斂在這裡。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

from . import executor, policy
from .events import EventLog


@dataclass
class HandlerResult:
    ok: bool
    artifact: str | None = None     # 產物絕對路徑
    summary: str = ""
    trace: dict = field(default_factory=dict)   # 給 fallback payload 用的執行軌跡
    failure_reason: str | None = None


@dataclass
class Context:
    spec: dict
    params: dict
    log: EventLog
    read_roots: list[Path]               # 唯讀掃描允許的 root
    write_allowlist: list[str]           # 寫入允許目錄（相對 framework 根）
    allow_network: bool = False

    def run_cmd(self, argv: list[str], *, cwd: Path | None = None, timeout: int = 60):
        """跑一條受控命令；雙層 Policy Gate（讀路徑 + 命令）皆過才執行，否則寫 blocked 事件。"""
        # 第一層：cwd 必須在唯讀 root 內（反路徑穿越）
        if cwd is not None:
            d = policy.check_read_path(str(cwd), self.read_roots)
            if not d.allow:
                self.log.emit("blocked", ok=False, reason=d.reason, detail={"argv": argv})
                return executor.ExecResult(False, argv, blocked_reason=d.reason)
        # 第一層：命令建構前檢查（網路/破壞/注入）
        cd = policy.check_command(argv, allow_network=self.allow_network)
        if not cd.allow:
            self.log.emit("blocked", ok=False, reason=cd.reason, detail={"argv": argv})
            return executor.ExecResult(False, argv, blocked_reason=cd.reason)
        # 第二層：executor 內再檢一次後才真的跑
        res = executor.run(argv, cwd=cwd, allow_network=self.allow_network, timeout=timeout)
        self.log.emit("tool_exec", ok=res.ok,
                      detail={"argv": argv, "rc": res.returncode,
                              "blocked": res.blocked_reason})
        return res

    def write_output(self, rel_path: str, content: str) -> Path:
        """經 Policy Gate 解析寫入目標（白名單防護），寫檔並記事件。"""
        target = policy.resolve_write_target(rel_path, self.write_allowlist)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.log.emit("artifact_written", ok=True, detail={"path": str(target)})
        return target
