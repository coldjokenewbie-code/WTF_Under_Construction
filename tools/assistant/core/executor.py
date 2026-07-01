"""受控 executor — 所有 shell 執行的唯一出口。

鐵則：
- 只接受 argv list，永不 shell=True（杜絕注入）。
- 執行前再過一次 Policy Gate（雙層的第二層）。
- 限制 cwd、套用 timeout、捕捉 stdout/stderr。
"""
from __future__ import annotations
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import policy


@dataclass
class ExecResult:
    ok: bool
    argv: list[str]
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    blocked_reason: str | None = None
    trace: dict = field(default_factory=dict)


def run(argv: list[str], *, cwd: Path | None = None, allow_network: bool = False,
        timeout: int = 60) -> ExecResult:
    decision = policy.check_command(argv, allow_network=allow_network)
    if not decision.allow:
        return ExecResult(False, argv, blocked_reason=decision.reason)
    try:
        proc = subprocess.run(
            argv, cwd=str(cwd) if cwd else None,
            capture_output=True, text=True, timeout=timeout, shell=False,
        )
        return ExecResult(
            ok=(proc.returncode == 0), argv=argv, returncode=proc.returncode,
            stdout=proc.stdout, stderr=proc.stderr,
        )
    except subprocess.TimeoutExpired:
        return ExecResult(False, argv, blocked_reason=f"逾時 {timeout}s")
    except FileNotFoundError:
        return ExecResult(False, argv, blocked_reason=f"找不到執行檔：{argv[0]}")
