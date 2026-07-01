"""handler: kiosk_build_verify

對一個 kiosk/HTML 頁面做「視覺自驗」：headless 載入 → 截圖 → 對 spec 的
visual_assertions 逐項機檢（斷圖/console error/溢出/字數上限/元素存在/垂直置中）。
全程零 LLM；只渲染本地檔，不操作活站。沿用機器既有 playwright（免重裝）。

斷言不過 → HandlerResult.ok=False，由 orchestrator 帶軌跡退回 LLM 修（fallback），
修完再驗，全過才交付——這就是「不交一看就不符合需求的成品」的閘。
"""
from __future__ import annotations
import html
import json
from datetime import datetime
from pathlib import Path

from ..core.context import Context, HandlerResult
from ..core.paths import ASSISTANT_ROOT, OUTPUTS_DIR

SCRIPT = ASSISTANT_ROOT / "runtime" / "verify_page.cjs"
_PW_FALLBACKS = [
    Path("/Users/coma/Git_work/Assembly_Plant_Mobile_Guide/node_modules/playwright"),
]


def _find_playwright(page_path: Path) -> str | None:
    for parent in [page_path.resolve(), *page_path.resolve().parents]:
        cand = parent / "node_modules" / "playwright"
        if cand.exists():
            return str(cand)
    for fb in _PW_FALLBACKS:
        if fb.exists():
            return str(fb)
    return None


def run(spec: dict, ctx: Context) -> HandlerResult:
    p = spec.get("params", {})
    page = p.get("page")
    if not page:
        return HandlerResult(False, failure_reason="spec.params.page 未指定")
    page_path = Path(page)
    if not page_path.is_absolute():
        page_path = (ASSISTANT_ROOT.parent.parent / page)  # 相對 WTF repo 根
    if not page_path.exists():
        return HandlerResult(False, failure_reason=f"頁面不存在：{page_path}")

    pw = _find_playwright(page_path)
    if not pw:
        return HandlerResult(False, failure_reason="找不到 playwright 套件（需 node_modules/playwright）")

    assertions = spec.get("visual_assertions", [])
    vp = p.get("viewport", {"w": 1080, "h": 1920})
    settle = int(p.get("settle_ms", 800))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    asrt_path = ctx.write_output(f"data/kiosk_assertions_{stamp}.json",
                                 json.dumps(assertions, ensure_ascii=False))
    out_dir = OUTPUTS_DIR / f"kiosk-verify_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    res = ctx.run_cmd(
        ["node", str(SCRIPT), pw, str(page_path), str(asrt_path), str(out_dir),
         str(vp.get("w", 1080)), str(vp.get("h", 1920)), str(settle)],
        timeout=90,
    )
    if not res.ok:
        return HandlerResult(False, failure_reason=f"node 執行失敗：{res.blocked_reason or res.stderr[:300]}")

    line = next((l for l in reversed(res.stdout.splitlines()) if l.strip().startswith("{")), "")
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return HandlerResult(False, failure_reason=f"無法解析驗證輸出：{res.stdout[:300]}")
    if not data.get("ok"):
        return HandlerResult(False, failure_reason=f"驗證器錯誤：{data.get('error')}")

    checks = data["assertions"]
    failed = [c for c in checks if not c["pass"]]
    report = _render_report(page_path, data.get("screenshot"), checks, stamp)
    report_path = ctx.write_output(f"outputs/kiosk-verify_{stamp}/report.html", report)

    ok = len(failed) == 0
    return HandlerResult(
        ok=ok, artifact=str(report_path),
        summary=f"{len(checks)-len(failed)}/{len(checks)} 視覺斷言通過"
                + ("" if ok else f"；不過：{', '.join(c['rule'] for c in failed)}"),
        trace={"failed": failed, "screenshot": data.get("screenshot"), "page": str(page_path)},
        failure_reason=None if ok else f"{len(failed)} 項視覺斷言未過",
    )


def _render_report(page_path, shot, checks, stamp) -> str:
    rows = ""
    for c in checks:
        ico = "✅" if c["pass"] else "❌"
        color = "#2e7d32" if c["pass"] else "#c62828"
        rows += (f'<tr><td>{ico}</td><td><code>{html.escape(c["rule"])}</code>'
                 f'<br><span style="color:#999;font-size:12px">{html.escape(str(c.get("selector") or ""))}</span></td>'
                 f'<td style="color:{color}">{html.escape(c["detail"])}</td></tr>')
    shot_rel = Path(shot).name if shot else ""
    npass = sum(1 for c in checks if c["pass"])
    verdict = "✅ 全數通過，可交付" if npass == len(checks) else f"❌ {len(checks)-npass} 項未過，禁止交付（需修正後重驗）"
    return f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<title>視覺自驗報告 {stamp}</title>
<style>body{{font-family:-apple-system,"PingFang TC",sans-serif;max-width:900px;margin:20px auto;
padding:0 16px;color:#1a1a1a}}h1{{font-size:20px}}.v{{font-size:16px;font-weight:700;margin:8px 0 16px}}
table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #eee;padding:8px 10px;text-align:left;vertical-align:top}}
th{{background:#f5f5f5}}code{{background:#f0f0f0;padding:1px 5px;border-radius:4px}}
img{{max-width:320px;border:1px solid #ddd;border-radius:8px;float:right;margin:0 0 10px 16px}}
.meta{{color:#888;font-size:13px}}</style></head><body>
<h1>🔍 kiosk 視覺自驗報告</h1>
<div class="meta">頁面：{html.escape(str(page_path))}｜{stamp}｜零 LLM</div>
<div class="v">{verdict}</div>
{f'<img src="{shot_rel}" alt="screenshot">' if shot_rel else ''}
<table><tr><th></th><th>斷言</th><th>結果</th></tr>{rows}</table>
<p class="meta">由 tools/assistant handler <code>kiosk_build_verify</code> 自動產生 · 截圖 + 逐項機檢</p>
</body></html>"""
