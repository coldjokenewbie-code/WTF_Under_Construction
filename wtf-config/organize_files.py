#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
organize_files.py — 依 GLOBAL.md 規則整理檔案歸位
真相源(SSOT): wtf-config/GLOBAL.md「檔案、命名與輸出規範」

兩段式安全設計:
  python organize_files.py            預設 dry-run，只印計畫，不動任何檔
  python organize_files.py <專案名>   只規劃單一專案
  python organize_files.py --apply    實際執行（只搬 AUTO 項；MANUAL 永不自動動）

分級:
  AUTO   — 機械式、零歧義，--apply 時執行
           · output/ 目錄 → outputs/
           · 根目錄臨時腳本 _*.{mjs,js,py,ts} → tools/
           · 根目錄截圖類圖檔（_*、thumbnails、含 qa）→ outputs/_shared/_screenshots/
           · 同組多版本檔的「非最新版」→ outputs/archive/
  MANUAL — 有業務語意、可能猜錯，只印建議，永不自動搬（人工拍板）
           · 根目錄成果/素材文件（pptx/docx/xlsx/pdf）— 該歸哪個子專案 outputs/<子專案>/ 待判
           · 同組多版本的「最新版」放哪個子專案夾 — outputs/<子專案>/
           · _context 檔名違規（改名涉及語意）

搬檔護欄: 只搬不刪、同名不覆蓋（衝突跳過回報）、目的夾不存在才建立。
"""
import sys
import re
import shutil
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[2]
PROJECTS_DIR = ROOT / "projects"

SCRIPT_EXT = {".mjs", ".js", ".ts", ".py"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
DOC_EXT = {".pptx", ".docx", ".xlsx", ".pdf", ".csv"}
ROOT_ALLOW = {"claude.md", "agents.md", "gemini.md", "codex.md", "readme.md",
              "index.html", "package.json", "package-lock.json",
              "requirements.txt", ".gitignore", ".gitattributes", ".gitkeep",
              "tsconfig.json", "vite.config.js"}
VERSION_RE = re.compile(r"[vV](\d+)(?:\.(\d+))?")


def rel(p):
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def version_key(name):
    """回傳 (group_key, (主,次)) 或 None。group_key = 去掉版本字串後的檔名+副檔名。"""
    m = VERSION_RE.search(name)
    if not m:
        return None
    major = int(m.group(1))
    minor = int(m.group(2)) if m.group(2) else 0
    group = (name[:m.start()] + name[m.end():]).lower()
    return group, (major, minor)


def plan_project(d):
    auto = []    # (src, dest, 說明)
    manual = []  # (src, 建議, 原因)

    # 1. output/ → outputs/（一律 MANUAL：目錄改名會打斷程式碼硬路徑引用，
    #    如 app.js/settings.json 內 output/xxx；須先 grep 確認無引用再改）
    out_s = d / "output"
    if out_s.is_dir():
        if (d / "outputs").is_dir():
            manual.append((out_s, d / "outputs", "outputs/ 已存在，需人工合併（避免覆蓋）"))
        else:
            manual.append((out_s, d / "outputs",
                           "目錄改名；先 grep 確認無程式碼引用 output/ 路徑再改"))

    # 收集根目錄散落檔
    root_files = [f for f in d.iterdir() if f.is_file()
                  and f.name.lower() not in ROOT_ALLOW]

    # 2. 版本分組（根目錄）：非最新版 → outputs/OLD/，最新版標 MANUAL
    groups = {}
    for f in root_files:
        vk = version_key(f.name)
        if vk:
            groups.setdefault(vk[0], []).append((vk[1], f))
    versioned = set()
    for gkey, items in groups.items():
        if len(items) < 2:
            continue
        items.sort()  # 依版本升冪
        newest = items[-1][1]
        for _, f in items[:-1]:
            auto.append((f, d / "outputs" / "archive" / f.name, "舊版歸檔"))
            versioned.add(f)
        manual.append((newest, "outputs/<子專案>/", "同組最新版，歸哪個子專案待判"))
        versioned.add(newest)

    # 3/4. 其餘散落檔
    for f in root_files:
        if f in versioned:
            continue
        ext = f.suffix.lower()
        low = f.name.lower()
        if ext in SCRIPT_EXT and low.startswith("_"):
            auto.append((f, d / "tools" / f.name, "臨時/審查腳本歸 tools"))
        elif ext in IMG_EXT and (low.startswith("_") or "thumbnail" in low or "qa" in low):
            auto.append((f, d / "outputs" / "_shared" / "_screenshots" / f.name, "截圖歸位"))
        elif ext in DOC_EXT:
            manual.append((f, "outputs/<子專案>/ 或 outputs/_shared/", "業務文件，歸哪個子專案待判"))
        elif ext in IMG_EXT:
            manual.append((f, "outputs/_shared/_screenshots/ 或 outputs/<子專案>/", "圖檔用途待判"))

    return auto, manual


def do_move(src, dest):
    """只搬不刪、同名不覆蓋。回傳 (ok, 訊息)。"""
    if dest.exists():
        return False, "目的已存在，跳過（不覆蓋）"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    return True, "已搬移"


def main():
    args = [a for a in sys.argv[1:]]
    apply = "--apply" in args
    args = [a for a in args if a != "--apply" and a != "--dry-run"]
    only = args[0] if args else None

    if not PROJECTS_DIR.exists():
        sys.exit(f"[錯誤] 找不到 projects 目錄: {PROJECTS_DIR}")
    dirs = sorted([p for p in PROJECTS_DIR.iterdir() if p.is_dir()])
    if only:
        dirs = [p for p in dirs if p.name == only]
        if not dirs:
            sys.exit(f"[錯誤] 找不到專案: {only}")

    mode = "APPLY（實際搬檔）" if apply else "DRY-RUN（只印計畫，不動檔）"
    print(f"模式: {mode}")
    print(f"範圍: {PROJECTS_DIR}\n")

    tot_auto = tot_manual = tot_moved = tot_skip = 0
    for d in dirs:
        auto, manual = plan_project(d)
        if not auto and not manual:
            continue
        print(f"● {d.name}")
        for src, dest, note in auto:
            tot_auto += 1
            dest_disp = rel(dest) if isinstance(dest, Path) else dest
            if apply:
                ok, msg = do_move(src, dest)
                tot_moved += ok
                tot_skip += (not ok)
                tag = "✓搬移" if ok else "⤼跳過"
                print(f"   [AUTO {tag}] {src.name} → {dest_disp}  ({msg})")
            else:
                print(f"   [AUTO] {src.name} → {dest_disp}  — {note}")
        for src, sugg, reason in manual:
            tot_manual += 1
            name = src.name if isinstance(src, Path) else str(src)
            print(f"   [MANUAL] {name} → 建議 {sugg}  — {reason}（人工拍板）")
        print()

    print("--- 統計 ---")
    print(f"  AUTO 計畫: {tot_auto}　MANUAL 待人工: {tot_manual}")
    if apply:
        print(f"  實際搬移: {tot_moved}　跳過(衝突): {tot_skip}")
    else:
        print("  本次未動任何檔。確認無誤後加 --apply 執行（只搬 AUTO）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
