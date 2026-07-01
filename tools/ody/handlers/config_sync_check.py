"""handler: config_sync_check

跑 wtf-config/sync_config.py check（唯讀）回報跨工具設定是否與 SSOT 一致。
零 LLM、不寫任何設定（check 子命令本身唯讀）。
"""
from __future__ import annotations
import sys
from datetime import datetime

from ..core.context import Context, HandlerResult
from ..core.paths import WTF_ROOT


def run(spec: dict, ctx: Context) -> HandlerResult:
    script = WTF_ROOT / "wtf-config" / "sync_config.py"
    if not script.exists():
        return HandlerResult(False, failure_reason=f"找不到 sync_config.py：{script}")

    res = ctx.run_cmd([sys.executable, str(script), "check"], cwd=WTF_ROOT, timeout=60)
    output = res.stdout or res.stderr or res.blocked_reason or ""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = ctx.write_output(f"outputs/config-sync_{stamp}.txt", output)

    consistent = "全部與真相源一致" in output
    return HandlerResult(
        ok=res.ok, artifact=str(target),
        summary=("設定一致" if consistent else "設定有差異，見產物"),
        trace={"consistent": consistent, "rc": res.returncode},
        failure_reason=None if res.ok else "sync_config check 非零退出",
    )
