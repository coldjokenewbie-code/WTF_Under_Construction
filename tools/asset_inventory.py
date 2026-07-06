#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""大資產清單生成器。

在專案 repo 根執行：python3 asset_inventory.py [--min-mb 20]
掃描被 .gitignore 排除的檔案（≥門檻），合併既有紀錄後重寫：
  assets/清單.md        — 給 AI 與跨機查詢（檔名/大小/哪台機器有）
  assets/資產櫥窗.html   — 給人：縮圖網格，點擊以本機路徑開啟

「哪台有」按 hostname 累積：本機掃到＝登記本機；本機沒有但清單記過別台＝保留該紀錄。
"""
import argparse, html, json, os, socket, subprocess, sys
from pathlib import Path

def ignored_files(root: Path, min_bytes: int):
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--others", "--ignored",
         "--exclude-standard", "-z"],
        capture_output=True, text=True, check=True).stdout
    for rel in filter(None, out.split("\0")):
        p = root / rel
        if p.is_file() and p.stat().st_size >= min_bytes:
            yield rel.replace("\\", "/"), p.stat().st_size

def load_registry(md: Path):
    reg = {}
    if md.exists():
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.startswith("| ") and not line.startswith("| 檔案"):
                cols = [c.strip() for c in line.strip("|").split("|")]
                if len(cols) >= 3 and cols[0] != "---":
                    reg[cols[0]] = {"size": cols[1], "hosts": set(cols[2].split("、")) - {""}}
    return reg

def fmt_size(n): return f"{n/1048576:.0f}MB" if n >= 1048576 else f"{n//1024}KB"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-mb", type=float, default=20)
    args = ap.parse_args()
    root = Path.cwd()
    if not (root / ".git").exists():
        sys.exit("要在專案 repo 根目錄執行")
    host = socket.gethostname().split(".")[0]
    assets_dir = root / "assets"; assets_dir.mkdir(exist_ok=True)
    md = assets_dir / "清單.md"
    reg = load_registry(md)

    local = dict(ignored_files(root, int(args.min_mb * 1048576)))
    for rel, size in local.items():
        e = reg.setdefault(rel, {"size": "", "hosts": set()})
        e["size"] = fmt_size(size); e["hosts"].add(host)

    rows = "\n".join(
        f"| {rel} | {e['size']} | {'、'.join(sorted(e['hosts']))} |"
        for rel, e in sorted(reg.items()))
    md.write_text(
        "# 大資產清單（自動生成，勿手改）\n"
        f"> 產生：`python3 <WTF_ROOT>/tools/asset_inventory.py`；本機={host}；"
        "檔案本體被 .gitignore 排除、不隨 git 同步，本表隨 git 同步。\n\n"
        "| 檔案 | 大小 | 哪台有 |\n|---|---|---|\n" + rows + "\n",
        encoding="utf-8")

    IMG = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    cards = []
    for rel, e in sorted(reg.items()):
        here = rel in local
        thumb = (f'<img src="../{html.escape(rel)}" loading="lazy">'
                 if here and Path(rel).suffix.lower() in IMG
                 else f'<div class="ph">{html.escape(Path(rel).suffix or "?")}</div>')
        body = (f'<a href="../{html.escape(rel)}">{thumb}</a>' if here
                else f'{thumb}<div class="miss">本機無（在：{html.escape("、".join(sorted(e["hosts"])) or "?")}）</div>')
        cards.append(f'<figure>{body}<figcaption>{html.escape(rel)}<br>'
                     f'<small>{e["size"]}</small></figcaption></figure>')
    (assets_dir / "資產櫥窗.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>資產櫥窗</title><style>'
        'body{font-family:system-ui;margin:20px;display:grid;'
        'grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px}'
        'figure{margin:0;border:1px solid #ccc;border-radius:8px;padding:8px}'
        'img,.ph{width:100%;height:110px;object-fit:cover;border-radius:4px}'
        '.ph{display:flex;align-items:center;justify-content:center;background:#eee;color:#888}'
        '.miss{color:#b00;font-size:12px}figcaption{font-size:12px;word-break:break-all}'
        '</style>' + "".join(cards) or "（無資產）", encoding="utf-8")
    print(f"{len(reg)} 筆 → assets/清單.md、assets/資產櫥窗.html（本機掃到 {len(local)} 筆）")

if __name__ == "__main__":
    main()
