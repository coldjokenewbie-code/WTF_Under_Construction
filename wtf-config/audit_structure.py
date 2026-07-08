#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_structure.py — 工作區結構／檔名稽核（只報告，絕不動檔）
真相源(SSOT): wtf-config/GLOBAL.md「檔案、命名與輸出規範」

用途: 掃描所有專案，依 GLOBAL.md 規則回報違規，供人工確認後再整理。
      本腳本永不新增/搬移/刪除任何檔案。

子命令:
  python audit_structure.py            掃描全部專案
  python audit_structure.py <專案名>   只掃單一專案

檢查項:
  1. 標準子夾缺漏（_context/rules/outputs/tools）
  2. output 單數資料夾（規則為複數 outputs）
  3. 缺 _context/INDEX.md（現況總覽）
  4. _context 檔名違規（通用名、Handoff 異體、不符「類型_日期_主題」）
  5. 專案根目錄散落檔（素材/office/截圖/臨時腳本應歸子夾）
  6. 版本平鋪（vX 多版本並存，舊版應進 outputs/OLD/）
"""
import sys
import re
from pathlib import Path

# Windows 主控台預設 cp950，中文輸出會亂碼；強制 UTF-8。
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = Path(__file__).resolve().parent          # .../wtf-config
ROOT = SCRIPT_DIR.parents[2]                           # .../Claude_cowork
PROJECTS_DIR = ROOT / "projects"

STD_SUBDIRS = ["_context", "rules", "outputs", "tools"]

# _context 內允許的檔名前綴（依 GLOBAL.md 命名慣例）
CTX_PREFIXES = ("INDEX", "PRD_", "Plan_", "TaskLog_", "Handover_",
                "lessons-learned", "about-me", "ClosedTaskLog_")
CTX_ALLOWED_DIRS = ("archive", "rules")

# 通用名／異體（違規）
GENERIC_NAMES = {"prd.md", "task.md", "tasks.md", "note.md", "notes.md",
                 "todo.md", "readme.md", "doc.md", "plan.md", "index.md",
                 "handoff.md", "handoff_prompt.md", "prompt.md"}
HANDOFF_VARIANT = re.compile(r"handoff", re.IGNORECASE)
DATED_PATTERN = re.compile(r"_(\d{4})-(\d{2})-(\d{2})_")

# 散落根目錄的檔案副檔名（應歸子夾）
LOOSE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg",
             ".pptx", ".docx", ".xlsx", ".pdf", ".mp4", ".mov",
             ".mjs", ".csv", ".json"}
# 根目錄允許的入口/設定檔
ROOT_ALLOW = {"claude.md", "agents.md", "gemini.md", "codex.md",
              "readme.md", "index.html", "package.json", "package-lock.json",
              "requirements.txt", ".gitignore", ".gitattributes",
              ".gitkeep", "tsconfig.json", "vite.config.js"}
VERSION_PATTERN = re.compile(r"[vV]\d+(\.\d+)?")


def rel(p):
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def audit_project(d):
    findings = []  # (等級, 訊息)  等級: WARN / INFO

    # 1. 標準子夾缺漏
    has_output_singular = (d / "output").is_dir()
    for sub in STD_SUBDIRS:
        if not (d / sub).is_dir():
            if sub == "outputs" and has_output_singular:
                continue  # 由檢查 2 處理
            findings.append(("INFO", f"缺子夾 {sub}/"))

    # 2. output 單數
    if has_output_singular:
        findings.append(("WARN", "存在單數 output/，規則為複數 outputs/（待改名）"))

    # 3. 缺 INDEX.md
    ctx = d / "_context"
    if ctx.is_dir() and not (ctx / "INDEX.md").exists():
        findings.append(("INFO", "缺 _context/INDEX.md（現況總覽）"))

    # 4. _context 檔名違規
    if ctx.is_dir():
        for f in sorted(ctx.iterdir()):
            if f.is_dir():
                continue
            name = f.name
            low = name.lower()
            if low in GENERIC_NAMES and not name.startswith(CTX_PREFIXES):
                findings.append(("WARN", f"_context/{name}：通用檔名，違反「類型_日期_主題」"))
                continue
            if HANDOFF_VARIANT.search(name) and not name.startswith("Handover_"):
                findings.append(("WARN", f"_context/{name}：Handoff 異體，統一寫 Handover_"))
                continue
            if name.startswith(CTX_PREFIXES):
                # 需日期的型別缺日期
                if name.startswith(("PRD_", "Plan_", "TaskLog_", "Handover_")) \
                        and not DATED_PATTERN.search(name):
                    findings.append(("WARN", f"_context/{name}：缺 YYYY-MM-DD 日期段"))
                continue
            if low.endswith(".md"):
                findings.append(("INFO", f"_context/{name}：未分類型別（人工確認是否需歸檔/改名）"))

    # 5. 根目錄散落檔
    for f in sorted(d.iterdir()):
        if f.is_dir():
            continue
        low = f.name.lower()
        if low in ROOT_ALLOW:
            continue
        if f.suffix.lower() in LOOSE_EXT or low.startswith("_"):
            findings.append(("WARN", f"根目錄散落檔 {f.name}（建議歸 outputs/_shared/ 或 tools/ 或 outputs/<子專案>/）"))

    # 6. 版本平鋪（同層多個 vX）
    for base in [d, d / "outputs", d / "output"]:
        if not base.is_dir():
            continue
        versions = [f.name for f in base.iterdir()
                    if VERSION_PATTERN.search(f.name) and "OLD" not in f.parts]
        if len(versions) >= 2:
            findings.append(("WARN",
                f"{rel(base)} 有多版本平鋪（{len(versions)} 個），舊版應進 outputs/OLD/"))

    return findings


def main():
    if not PROJECTS_DIR.exists():
        sys.exit(f"[錯誤] 找不到 projects 目錄: {PROJECTS_DIR}")

    only = sys.argv[1] if len(sys.argv) > 1 else None
    dirs = sorted([p for p in PROJECTS_DIR.iterdir() if p.is_dir()])
    if only:
        dirs = [p for p in dirs if p.name == only]
        if not dirs:
            sys.exit(f"[錯誤] 找不到專案: {only}")

    print(f"稽核範圍: {PROJECTS_DIR}")
    print("（只報告，不動任何檔案）\n")

    total_warn = total_info = 0
    for d in dirs:
        findings = audit_project(d)
        warn = [f for f in findings if f[0] == "WARN"]
        info = [f for f in findings if f[0] == "INFO"]
        total_warn += len(warn)
        total_info += len(info)
        if not findings:
            print(f"  ✓ {d.name}：無違規")
            continue
        print(f"  ● {d.name}：{len(warn)} WARN / {len(info)} INFO")
        for level, msg in warn:
            print(f"      ✗ [WARN] {msg}")
        for level, msg in info:
            print(f"      · [INFO] {msg}")

    print(f"\n--- 統計 ---")
    print(f"  WARN（應處理）: {total_warn}")
    print(f"  INFO（建議補齊）: {total_info}")
    print("\n下一步：人工確認後再整理（搬檔策略待定，本腳本不動檔）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
