"""handler: project_digest

掃 wtf-config/projects-registry.md → 取本機 hostname 欄的各專案路徑 →
對每個 git repo 跑唯讀 `git log` → 彙整成 HTML 動態摘要。
全程零 LLM、唯讀、不改任何 repo。
"""
from __future__ import annotations
import html
import socket
from datetime import datetime
from pathlib import Path

from ..core import policy
from ..core.context import Context, HandlerResult
from ..core.paths import WTF_ROOT


def _parse_registry(md: str, hostname: str) -> list[tuple[str, str]]:
    """回傳 [(project, local_path)]，取欄頭最匹配本機 hostname 的那欄。"""
    rows = [l for l in md.splitlines() if l.strip().startswith("|")]
    if len(rows) < 2:
        return []
    header = [c.strip() for c in rows[0].strip("|").split("|")]
    # 找最匹配本機的欄（精確 > 前綴）
    host_l = hostname.lower()
    col_idx = None
    for i, h in enumerate(header):
        if h.lower() == host_l:
            col_idx = i
            break
    if col_idx is None:
        for i, h in enumerate(header):
            hl = h.lower()
            if hl and (host_l.startswith(hl) or hl.startswith(host_l)):
                col_idx = i
                break
    if col_idx is None:
        return []
    out = []
    for r in rows[2:]:  # 跳過 header + 分隔列
        cells = [c.strip() for c in r.strip("|").split("|")]
        if len(cells) <= col_idx:
            continue
        proj, path = cells[0], cells[col_idx]
        if not path or path.startswith("（"):  # 全形括號＝未部署
            continue
        out.append((proj, path))
    return out


def run(spec: dict, ctx: Context) -> HandlerResult:
    params = spec.get("params", {})
    since = params.get("since", "14 days ago")
    limit = int(params.get("limit", 5))

    hostname = socket.gethostname()
    reg_path = WTF_ROOT / "wtf-config" / "projects-registry.md"
    if not reg_path.exists():
        return HandlerResult(False, failure_reason=f"找不到 registry：{reg_path}")

    projects = _parse_registry(reg_path.read_text(encoding="utf-8"), hostname)
    ctx.log.emit("handler_result", ok=True,
                 detail={"phase": "parsed_registry", "host": hostname,
                         "n_projects": len(projects)})

    sections = []
    scanned = skipped = 0
    for proj, path in projects:
        rd = policy.check_read_path(path, ctx.read_roots)
        if not rd.allow:
            skipped += 1
            sections.append((proj, path, "skip", [f"略過（不在允許 root）：{rd.reason}"]))
            continue
        repo = Path(path)
        if not repo.exists() or not (repo / ".git").exists():
            skipped += 1
            sections.append((proj, path, "skip", ["略過（非本機 git repo 或路徑不存在）"]))
            continue
        # 用 ASCII unit separator(0x1f) 當欄位分隔，避開 `|`（Policy Gate 視 `|` 為注入字元）
        res = ctx.run_cmd(
            ["git", "-C", str(repo), "log", f"--since={since}",
             "-n", str(limit), "--date=short", "--format=%h%x1f%ad%x1f%s"],
            timeout=30,
        )
        if not res.ok:
            skipped += 1
            sections.append((proj, path, "err", [res.blocked_reason or res.stderr.strip() or "git log 失敗"]))
            continue
        scanned += 1
        commits = [l for l in res.stdout.splitlines() if l.strip()]
        sections.append((proj, path, "ok", commits if commits else ["（區間內無 commit）"]))

    artifact_html = _render_html(since, limit, hostname, scanned, skipped, sections)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = ctx.write_output(f"outputs/project-digest_{stamp}.html", artifact_html)

    return HandlerResult(
        ok=True, artifact=str(target),
        summary=f"掃 {scanned} repo、略過 {skipped}，since={since}",
        trace={"scanned": scanned, "skipped": skipped, "since": since},
    )


def _render_html(since, limit, host, scanned, skipped, sections) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = []
    for proj, path, status, lines in sections:
        badge = {"ok": "#2e7d32", "skip": "#9e9e9e", "err": "#c62828"}.get(status, "#555")
        items = []
        for ln in lines:
            parts = ln.split("\x1f")
            if len(parts) == 3:
                h, d, s = (html.escape(p) for p in parts)
                items.append(f'<li><code>{h}</code> <span class="d">{d}</span> {s}</li>')
            else:
                items.append(f'<li class="muted">{html.escape(ln)}</li>')
        rows.append(
            f'<section><h2><span class="dot" style="background:{badge}"></span>'
            f'{html.escape(proj)}</h2>'
            f'<div class="path">{html.escape(path)}</div>'
            f'<ul>{"".join(items)}</ul></section>'
        )
    return f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>專案動態摘要 — {now}</title>
<style>
 body{{font-family:-apple-system,"PingFang TC",sans-serif;max-width:880px;margin:24px auto;
  padding:0 16px;color:#1a1a1a;background:#fafafa;line-height:1.5}}
 h1{{font-size:22px}} .meta{{color:#666;font-size:13px;margin-bottom:20px}}
 section{{background:#fff;border:1px solid #eee;border-radius:10px;padding:14px 18px;margin:12px 0}}
 h2{{font-size:16px;margin:0 0 4px;display:flex;align-items:center}}
 .dot{{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:8px}}
 .path{{color:#999;font-size:12px;font-family:ui-monospace,monospace;margin-bottom:8px}}
 ul{{margin:6px 0 0;padding-left:18px}} li{{margin:3px 0;font-size:14px}}
 code{{background:#f0f0f0;padding:1px 5px;border-radius:4px;font-size:12px}}
 .d{{color:#888;font-size:12px;margin:0 6px}} .muted,.muted li{{color:#aaa;font-style:italic}}
 footer{{color:#aaa;font-size:12px;margin-top:24px;text-align:center}}
</style></head><body>
<h1>📊 專案動態摘要</h1>
<div class="meta">產生：{now}｜機器：{html.escape(host)}｜區間 since <b>{html.escape(str(since))}</b>、每 repo 取 {limit} 筆
 ｜掃描 {scanned}、略過 {skipped}｜<b>本檔由 assistant 框架零 LLM 產生</b></div>
{"".join(rows)}
<footer>generated by tools/assistant · deterministic handler <code>project_digest</code> · llm_calls=0</footer>
</body></html>"""
