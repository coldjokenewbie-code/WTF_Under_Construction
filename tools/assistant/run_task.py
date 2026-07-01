"""run_task — Orchestrator 進入點。

流程：載入 spec → schema 驗證 → 分類（本地優先路由）→ 命中 handler 跑確定性流程
（llm_calls=0）／未命中或失敗才走 Adapter fallback（預設 dry，不花 API）→
全程經 Policy Gate、寫結構化事件 → 產 artifact。

執行：
  python3 tools/assistant/run_task.py tools/assistant/tasks/project-digest.task.json
  python3 -m assistant.run_task <spec.json>          （tools/ 在 sys.path 時）
"""
from __future__ import annotations

# --- 允許「直接以腳本執行」：把 tools/ 加入 sys.path 後改用套件名重跑 ---
if __package__ in (None, ""):
    import os
    import runpy
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    runpy.run_module("assistant.run_task", run_name="__main__", alter_sys=True)
    sys.exit(0)

import argparse
import json
import uuid
from pathlib import Path

from .core import adapter, preflight, validate
from .core.context import Context
from .core.events import EventLog
from .core.paths import ASSISTANT_ROOT, SCHEMAS_DIR, WTF_ROOT, ensure_dirs
from .core import registry

_SPEC_SCHEMA = json.loads((SCHEMAS_DIR / "task_spec.schema.json").read_text(encoding="utf-8"))

DEFAULT_WRITE_ALLOWLIST = ["data", "outputs"]


def _default_read_roots() -> list[Path]:
    roots = [WTF_ROOT.parent]  # 同層 Git_work
    cloud = Path.home() / "Library" / "CloudStorage"
    if cloud.exists():
        roots.append(cloud)  # Google Drive 鏡像的 cowork 專案
    return roots


def load_spec(path: str) -> dict:
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    validate.validate(spec, _SPEC_SCHEMA)  # 不合即 raise
    return spec


def run(spec: dict, *, allow_llm: bool = False, backend: str = "claude",
        preflight_only: bool = False) -> dict:
    ensure_dirs()
    run_id = uuid.uuid4().hex[:8]
    log = EventLog(spec["id"], run_id)
    constraints = spec.get("constraints", {})
    llm_calls = 0

    log.emit("start", task_type=spec.get("task_type"), llm_calls=0,
             detail={"goal": spec.get("goal")})

    entry = registry.lookup(spec["task_type"])
    log.emit("classified", task_type=spec.get("task_type"),
             handler=(entry.task_type if entry else None),
             detail={"routed_to": "handler" if entry else "fallback"})

    # 硬規則：動工前先做前置授權評估，把需授權點一次攤開
    assessment = preflight.assess(spec, entry)
    print(preflight.render(assessment))
    log.emit("preflight", ok=assessment.clear,
             detail={"triggered": [c for c, _ in assessment.triggered],
                     "blocked": [c for c, _ in assessment.blocked]})
    if preflight_only:
        return {"task_id": spec["id"], "run_id": run_id, "preflight_only": True,
                "clear": assessment.clear,
                "blocked": [c for c, _ in assessment.blocked], "ok": assessment.clear}
    if not assessment.clear:
        # 未授權 → 不動工，等使用者一次談定
        log.emit("blocked", ok=False, reason="前置授權未通過",
                 detail={"need_approval": [c for c, _ in assessment.blocked]})
        log.emit("finish", ok=False, llm_calls=0,
                 detail={"summary": "前置授權未通過，未動工"})
        return {"task_id": spec["id"], "run_id": run_id, "llm_calls": 0,
                "resolved_by": None, "ok": False, "artifact": None,
                "summary": "前置授權未通過，未動工：需授權 "
                           + "、".join(c for c, _ in assessment.blocked)}

    ctx = Context(
        spec=spec,
        params=spec.get("params", {}),
        log=log,
        read_roots=_default_read_roots(),
        write_allowlist=constraints.get("write_allowlist", DEFAULT_WRITE_ALLOWLIST),
        allow_network=constraints.get("allow_network", False),
    )

    result = {"task_id": spec["id"], "run_id": run_id, "llm_calls": 0,
              "resolved_by": None, "ok": False, "artifact": None, "summary": ""}

    if entry is not None:
        # 本地優先：命中即跑確定性 handler，完全繞過 LLM
        hr = entry.handler(spec, ctx)
        log.emit("handler_result", handler=entry.task_type, ok=hr.ok, llm_calls=0,
                 detail={"summary": hr.summary, "artifact": hr.artifact})
        result.update(resolved_by="handler", ok=hr.ok, artifact=hr.artifact,
                      summary=hr.summary, llm_calls=0)

        if not hr.ok:
            # handler 失敗 → 準備 fallback payload（帶軌跡，避免重做）
            payload = adapter.FallbackPayload(
                goal=spec.get("goal", ""), context=spec.get("task_type", ""),
                handler_trace=hr.trace, failure_reason=hr.failure_reason or "handler 失敗",
                constraints=constraints,
            )
            allowed = allow_llm and constraints.get("allow_llm", False)
            ar = adapter.call(payload, backend=backend, dry_run=not allowed)
            llm_calls = 1 if ar.called else 0
            log.emit("fallback", ok=ar.called, llm_calls=llm_calls,
                     detail={"backend": ar.backend, "planned_argv": ar.planned_argv,
                             "note": ar.note})
            result.update(llm_calls=llm_calls,
                          summary=hr.summary + f"｜fallback({ar.note})")
    else:
        # 未命中 registry → 直接走 fallback（這類任務尚未本地化）
        payload = adapter.FallbackPayload(
            goal=spec.get("goal", ""), context=spec.get("task_type", ""),
            handler_trace={}, failure_reason="無對應確定性 handler（尚未本地化）",
            constraints=constraints,
        )
        allowed = allow_llm and constraints.get("allow_llm", False)
        ar = adapter.call(payload, backend=backend, dry_run=not allowed)
        llm_calls = 1 if ar.called else 0
        log.emit("fallback", ok=ar.called, llm_calls=llm_calls,
                 detail={"backend": ar.backend, "planned_argv": ar.planned_argv,
                         "note": ar.note})
        result.update(resolved_by="fallback", ok=ar.called, llm_calls=llm_calls,
                      summary=f"未命中 registry｜{ar.note}")

    log.emit("finish", ok=result["ok"], llm_calls=result["llm_calls"],
             handler=result["resolved_by"],
             detail={"artifact": result["artifact"], "summary": result["summary"]})
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="AI 中立自主任務助理 — Orchestrator")
    ap.add_argument("spec", help="task spec JSON 路徑")
    ap.add_argument("--allow-llm", action="store_true",
                    help="允許 fallback 真的呼叫 LLM（預設 dry，不花 API）")
    ap.add_argument("--backend", default="claude", choices=list(adapter.BACKENDS),
                    help="AI 中立：fallback 用哪個後端")
    ap.add_argument("--preflight", action="store_true",
                    help="只做前置授權評估、印出需授權清單，不動工")
    ap.add_argument("--dump-registry", action="store_true",
                    help="輸出 registry.json 契約後結束")
    args = ap.parse_args(argv)

    if args.dump_registry:
        print("registry contract →", registry.dump_contract())
        return 0

    spec = load_spec(args.spec)
    result = run(spec, allow_llm=args.allow_llm, backend=args.backend,
                 preflight_only=args.preflight)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
