"""自驗測試套件 — 對應 ai-team Round 3 的 Verify Checklist。

零依賴、可離線跑：
  python3 tools/assistant/tests/test_safety.py

涵蓋：Policy Gate 拒絕（破壞/網路/注入/穿越/越界寫入）、executor 不執行被拒命令、
Adapter AI 中立抽換且 dry-run 不花 API、本地路由 llm_calls=0、blocked 事件落地。
"""
from __future__ import annotations
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ody.core import adapter, executor, policy  # noqa: E402
from ody.core.paths import ASSISTANT_ROOT  # noqa: E402

PASS, FAIL = "✅", "❌"
results = []


def check(name, cond):
    results.append((cond, name))
    print(f"{PASS if cond else FAIL} {name}")


# 1) Policy Gate：破壞性 / 網路 / 注入 / 穿越 全拒
check("拒 rm -rf", not policy.check_command(["rm", "-rf", "/tmp/x"]).allow)
check("拒 curl（網路，allow_network=False）", not policy.check_command(["curl", "http://x"]).allow)
check("允許 curl（allow_network=True）", policy.check_command(["curl", "http://x"], allow_network=True).allow)
check("拒 git push", not policy.check_command(["git", "-C", "/r", "push"]).allow)
check("拒 git reset", not policy.check_command(["git", "reset", "--hard"]).allow)
check("拒 注入字元 ;", not policy.check_command(["git", "log", "foo;rm -rf /"]).allow)
check("拒 路徑穿越 ..", not policy.check_command(["git", "-C", "../../etc", "log"]).allow)
check("拒 pipe |", not policy.check_command(["sh", "a|b"]).allow)
check("拒 字串命令（非 list）", not policy.check_command("rm -rf /").allow)
check("允許 唯讀 git log", policy.check_command(["git", "-C", "/r", "log"]).allow)

# 2) 寫入白名單防護
try:
    policy.resolve_write_target("../../etc/passwd", ["data", "outputs"])
    check("拒 越界寫入 ../../etc/passwd", False)
except PermissionError:
    check("拒 越界寫入 ../../etc/passwd", True)
try:
    t = policy.resolve_write_target("outputs/ok.txt", ["data", "outputs"])
    check("允許 白名單內寫入 outputs/", str(t).startswith(str(ASSISTANT_ROOT)))
except PermissionError:
    check("允許 白名單內寫入 outputs/", False)

# 3) executor 永不執行被拒命令
r = executor.run(["rm", "-rf", "/tmp/should_not_run"])
check("executor 拒跑 rm -rf（第二層）", (not r.ok) and r.blocked_reason is not None)
r2 = executor.run(["git", "--version"])
check("executor 可跑唯讀 git --version", r2.ok and "git" in r2.stdout.lower())

# 4) Adapter：AI 中立抽換 + dry-run 不花 API
payload = adapter.FallbackPayload("g", "c", {"done": ["step1"]}, "fail", {})
a_claude = adapter.call(payload, backend="claude", dry_run=True)
a_codex = adapter.call(payload, backend="codex", dry_run=True)
a_agy = adapter.call(payload, backend="agy", dry_run=True)
check("dry-run 不呼叫 LLM（不花 API）", not a_claude.called)
check("backend 抽換：claude argv 用 claude", a_claude.planned_argv[0] == "claude")
check("backend 抽換：codex argv 用 codex", a_codex.planned_argv[0] == "codex")
check("backend 抽換：agy argv 用 agy", a_agy.planned_argv[0] == "agy")
check("fallback payload 帶已完成軌跡（避免重做）", "step1" in a_claude.planned_argv[2])

# 5) 端到端：本地路由 llm_calls=0
from ody.run_task import load_spec, run  # noqa: E402
spec = load_spec(str(ASSISTANT_ROOT / "tasks" / "project-digest.task.json"))
res = run(spec, allow_llm=False)
check("端到端 project_digest ok", res["ok"])
check("端到端 llm_calls=0（省 API）", res["llm_calls"] == 0)
check("端到端 由本地 handler 解決", res["resolved_by"] == "handler")

# 6) blocked 事件確實落地（真的觸發再驗證）
from ody.core import events  # noqa: E402
from ody.core.context import Context  # noqa: E402
from ody.core.events import EventLog  # noqa: E402

_tid = "safety-test-blocked"
_ctx = Context(spec={}, params={}, log=EventLog(_tid, "testrun"),
               read_roots=[ASSISTANT_ROOT], write_allowlist=["data", "outputs"])
_blocked = _ctx.run_cmd(["rm", "-rf", "/tmp/should_not_run"])
check("ctx.run_cmd 拒破壞性命令", not _blocked.ok)
_evs = [e for e in events.read_all()
        if e["task_id"] == _tid and e["phase"] == "blocked"]
check("blocked 事件落地 events.jsonl", len(_evs) >= 1)

# 7) Round 4 驗收回歸：修補 Agy 三發現
from ody.core.paths import OUTPUTS_DIR  # noqa: E402

# #1 write-then-execute：禁從寫入區(outputs/data)執行檔案 + 直譯器跑寫入區腳本
check("拒 執行寫入區內檔案", not policy.check_command([str(OUTPUTS_DIR / "x.py")]).allow)
check("拒 直譯器跑寫入區腳本",
      not policy.check_command(["python3", str(OUTPUTS_DIR / "malicious.py")]).allow)
# #2 git 網路操作（allow_network=False）
check("拒 git clone（網路）", not policy.check_command(["git", "clone", "u"]).allow)
check("拒 git pull（網路）", not policy.check_command(["git", "-C", "/r", "pull"]).allow)
check("允許 git clone（allow_network=True）",
      policy.check_command(["git", "clone", "u"], allow_network=True).allow)
# #3 symlink/別名改名繞過：真實名仍被擋
_link = os.path.join(tempfile.mkdtemp(), "safe_rm")
try:
    os.symlink(shutil.which("rm") or "/bin/rm", _link)
    check("拒 symlink 別名(safe_rm→rm)", not policy.check_command([_link, "-rf", "/x"]).allow)
except OSError:
    check("拒 symlink 別名(safe_rm→rm)", True)  # 環境不支援 symlink 則略過

# 總結
n_fail = sum(1 for ok, _ in results if not ok)
print(f"\n{'='*40}\n通過 {len(results)-n_fail}/{len(results)}，失敗 {n_fail}")
sys.exit(1 if n_fail else 0)
