"""learn — 從 events.jsonl 算「省 API / 複利」指標，並偵測重複 fallback 產出升級草案。

鐵則（呼應 Round 2/3 共識）：
- 只讀結構化事件 + metadata，不重讀對話（學習本身也要省）。
- 偵測到「同 task_type 重複 fallback」→ 產 `.draft` 升級草案，**不自動生效**（PO 審核）。
- 草案＝建議「把這類任務寫成確定性 handler/skill」，下次即可本地化、llm_calls→0。

執行：
  python3 tools/assistant/learn.py            # 印指標 + 產草案
  python3 -m assistant.learn
"""
from __future__ import annotations

if __package__ in (None, ""):
    import os
    import runpy
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    runpy.run_module("assistant.learn", run_name="__main__", alter_sys=True)
    sys.exit(0)

import json
from collections import defaultdict
from datetime import datetime

from .core.events import read_all
from .core.paths import DRAFTS_DIR, ensure_dirs

PROMOTE_THRESHOLD = 2  # 同類任務 fallback 達此次數 → 提升級草案


def compute_metrics(events: list[dict]) -> dict:
    finishes = [e for e in events if e["phase"] == "finish"]
    runs = len(finishes)
    total_llm = sum(e.get("llm_calls", 0) for e in finishes)
    by_handler = [e for e in finishes if e.get("handler") == "handler"]
    local_ok = [e for e in by_handler if e.get("ok")]

    tool_execs = [e for e in events if e["phase"] == "tool_exec"]
    blocks = [e for e in events if e["phase"] == "policy_decision"
              and e.get("decision") == "deny"]
    blocked_cmds = [e for e in tool_execs
                    if e.get("detail", {}).get("blocked")]
    total_cmd_attempts = len(tool_execs) + len(blocks)

    # 同 task_id 多次執行的 llm_calls 趨勢（複利證據）
    per_task = defaultdict(list)
    for e in finishes:
        per_task[e["task_id"]].append(e.get("llm_calls", 0))
    repeat_delta = {}
    for tid, calls in per_task.items():
        if len(calls) >= 2:
            repeat_delta[tid] = {"first": calls[0], "last": calls[-1],
                                 "runs": len(calls)}

    return {
        "runs": runs,
        "llm_calls_per_task": round(total_llm / runs, 3) if runs else 0,
        "local_resolution_rate": round(len(local_ok) / runs, 3) if runs else 0,
        "policy_block_rate": round((len(blocks) + len(blocked_cmds)) / total_cmd_attempts, 3)
        if total_cmd_attempts else 0,
        "repeat_task_cost_delta": repeat_delta or "n/a（需同任務 ≥2 次執行）",
        "script_promotion_rate": "n/a（需升級歷史；見 data/drafts/）",
        "regression_rate": "n/a（需 lesson 套用後錯誤標記）",
    }


def detect_promotions(events: list[dict]) -> list[dict]:
    """同 task_type 的 fallback 次數達門檻 → 列為升級候選。"""
    fb_by_type = defaultdict(int)
    goal_by_type = {}
    for e in events:
        if e["phase"] == "fallback":
            # fallback 事件本身不帶 task_type，回溯同 run 的 start
            pass
    # 用 start 事件補 task_type，並數該 run 是否有 fallback
    starts = {e["run_id"]: e for e in events if e["phase"] == "start"}
    fb_runs = {e["run_id"] for e in events if e["phase"] == "fallback"}
    for run_id in fb_runs:
        st = starts.get(run_id)
        if not st:
            continue
        tt = st.get("task_type", "unknown")
        fb_by_type[tt] += 1
        goal_by_type[tt] = st.get("detail", {}).get("goal", "")
    return [{"task_type": tt, "fallback_count": n, "goal": goal_by_type.get(tt, "")}
            for tt, n in fb_by_type.items() if n >= PROMOTE_THRESHOLD]


def write_drafts(promotions: list[dict]) -> list[str]:
    ensure_dirs()
    written = []
    for p in promotions:
        path = DRAFTS_DIR / f"promote_{p['task_type']}.draft.md"
        body = (
            f"# 升級草案（DRAFT，待 PO 審核，勿自動生效）\n"
            f"> 產生：{datetime.now().isoformat()}\n\n"
            f"- task_type：`{p['task_type']}`\n"
            f"- 目標：{p['goal']}\n"
            f"- 已 fallback {p['fallback_count']} 次（達門檻 {PROMOTE_THRESHOLD}）\n\n"
            f"## 建議\n"
            f"把此類任務寫成確定性 handler（`handlers/{p['task_type']}.py`）並註冊 registry，\n"
            f"下次即走本地優先路由、llm_calls→0。封裝前須過 Policy Gate + 最小測試\n"
            f"（固定輸入同輸出 / 拒危險輸入 / 能回報不確定）。\n"
        )
        path.write_text(body, encoding="utf-8")
        written.append(str(path))
    return written


def main():
    events = read_all()
    metrics = compute_metrics(events)
    promotions = detect_promotions(events)
    drafts = write_drafts(promotions)
    print(json.dumps({
        "metrics": metrics,
        "promotion_candidates": promotions,
        "drafts_written": drafts,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
