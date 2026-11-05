#!/usr/bin/env python3
"""減少無意義的權限提示（PO 2026-11-05 裁定）。由三藏親自執行（AI 改權限設定會被分類器擋）。

做三件事，全部先備份、只加不刪：
1. 全域 ~/.claude/settings.json：permissions.allow 加入唯讀／本機檢查類命令白名單（所有 session 生效）。
2. 南科再生水廠 ↔ 3Dstudy 兩專案 .claude/settings.local.json：permissions.additionalDirectories 互加對方路徑
   （跨專案讀素材不再問；已開著的 session 仍要 /add-dir 一次）。
3. 列出改了什麼。

用法：python3 workingfiles/outputs/_shared/_scripts/permission-prompt-reduce.py [--dry-run]
"""
import datetime
import json
import os
import shutil
import sys

HOME = os.path.expanduser("~")
GLOBAL = os.path.join(HOME, ".claude", "settings.json")
PROJECTS = ("/Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/"
            "其他電腦/tachart_ihuy/Claude_cowork/projects")
PAIRS = {"南科再生水廠": ["3Dstudy"], "3Dstudy": ["南科再生水廠"]}

# 唯讀或只碰本機 loopback 的命令；寫檔、刪檔、起服務、python 執行任意碼都不在內。
READ_ONLY = [
    "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(wc:*)",
    "Bash(grep:*)", "Bash(rg:*)", "Bash(sed -n:*)", "Bash(awk:*)", "Bash(cut:*)", "Bash(sort:*)", "Bash(uniq:*)",
    "Bash(find:*)", "Bash(stat:*)", "Bash(file:*)", "Bash(du:*)", "Bash(md5:*)", "Bash(shasum:*)",
    "Bash(diff:*)", "Bash(cmp:*)", "Bash(lsof:*)", "Bash(pgrep:*)", "Bash(ps:*)",
    "Bash(curl -s http://127.0.0.1:*)", "Bash(curl -sI http://127.0.0.1:*)",
    "Bash(curl -s -o /dev/null -w:*)", "Bash(curl -sS http://127.0.0.1:*)",
    "Bash(unzip -l:*)", "Bash(zipinfo:*)", "Bash(echo:*)", "Bash(printf:*)", "Bash(date:*)",
    "Bash(mkdir -p:*)", "Bash(git status:*)", "Bash(git log:*)", "Bash(git diff:*)", "Bash(git show:*)",
    "Bash(python3 -m json.tool:*)", "Bash(mdfind:*)", "Bash(which:*)",
]

DRY = "--dry-run" in sys.argv
TS = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(path, data):
    if DRY:
        return
    shutil.copy(path, f"{path}.{TS}.bak")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    load(tmp)  # 寫壞就不換檔
    os.replace(tmp, path)


def main():
    # 1. 全域 allow
    if os.path.exists(GLOBAL):
        g = load(GLOBAL)
        allow = g.setdefault("permissions", {}).setdefault("allow", [])
        added = [r for r in READ_ONLY if r not in allow]
        allow.extend(added)
        save(GLOBAL, g)
        print(f"[全域] allow 新增 {len(added)} 條（原 {len(allow) - len(added)} 條）"
              + ("" if DRY else f"，備份 settings.json.{TS}.bak"))
    else:
        print("[全域] 找不到 ~/.claude/settings.json，略過")

    # 2. 專案 additionalDirectories
    for proj, others in PAIRS.items():
        path = os.path.join(PROJECTS, proj, ".claude", "settings.local.json")
        if not os.path.exists(path):
            print(f"[{proj}] 無 settings.local.json，略過")
            continue
        d = load(path)
        ad = d.setdefault("permissions", {}).setdefault("additionalDirectories", [])
        new = [os.path.join(PROJECTS, o) for o in others if os.path.join(PROJECTS, o) not in ad]
        ad.extend(new)
        save(path, d)
        print(f"[{proj}] additionalDirectories 新增 {[os.path.basename(n) for n in new]}"
              + ("" if DRY else f"，備份 settings.local.json.{TS}.bak"))

    print("完成。" + ("（dry-run，未寫入）" if DRY else "新開的 session 生效；已開著的 session 跨專案仍需 /add-dir 一次。"))


if __name__ == "__main__":
    main()
