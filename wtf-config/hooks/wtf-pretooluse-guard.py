#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wtf-pretooluse-guard.py — PreToolUse hook 規則引擎：機器攔截可觀測的制度違規。

設計原則：
  - 遵循度不靠自律：GLOBAL/AGENTS 中「工具呼叫可觀測」的規則在這裡硬性攔截，
    deny 理由會回饋給模型（官方：Claude receives it as feedback so it can adjust）。
  - fail-open：本腳本任何錯誤都放行（exit 0、無輸出），絕不因 guard 壞掉擋住正常工作。
  - 陸續新增規則：只改本檔 check()（黃區，走 maintenance-protocol 提案），sync 重部署，
    新 session 生效（hook 不熱載）。

輸入：argv[1]＝存有 PreToolUse stdin JSON 的暫存檔路徑（由 wtf-pretooluse-guard.sh 落地）。
輸出：違規時印 permissionDecision=deny 的 JSON；放行時無輸出。一律 exit 0。
正本：WTF repo wtf-config/hooks/（黃區）。部署與註冊見 wtf-pretooluse-guard.sh 檔尾。
"""
import json
import re
import sys

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# _context/ 命名慣例（GLOBAL.md「命名慣例」節）
NAMED_TYPES = r"(?:TaskLog|ClosedTaskLog|PRD|Plan|Handover)"
GOOD_NAME = re.compile(NAMED_TYPES + r"_\d{4}-\d{2}-\d{2}_.+\.md$")
GENERIC_NAMES = {"prd.md", "task.md", "tasklog.md", "plan.md",
                 "handover.md", "handoff.md", "worklog.md", "inbox.md"}


def norm_path(tool_input):
    p = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    return str(p).replace("\\", "/")


def check_write(tool, ti):
    p = norm_path(ti)
    if not p:
        return None
    base = p.rsplit("/", 1)[-1]

    # R1 歷史存證只讀（maintenance-protocol 紅區＋結案歸檔規範）
    if ("/_context/archive/" in p or p.startswith("_context/archive/")
            or "wtf-config/archive/" in p
            or base.startswith("ClosedTaskLog_")
            or p.endswith("playbooks/letter-from-fable5.md")):
        return ("R1 歷史存證只讀：_context/archive/、wtf-config/archive/、ClosedTaskLog_*、"
                "letter-from-fable5.md 禁改寫（maintenance-protocol 紅區）。"
                "結案歸檔請用 mv/git mv 搬移，不要在 archive 內直接寫檔。")

    # R2/R3 只驗新建檔（Write）：Edit 既有舊檔不追溯
    if tool == "Write" and ("/_context/" in p or p.startswith("_context/")):
        if base.lower() in GENERIC_NAMES:
            return ("R2 禁通用檔名：_context/ 檔案一律「類型_YYYY-MM-DD_主題.md」"
                    "（GLOBAL.md 命名慣例；INBOX.md 已廢除，走 /inbox 分流）。")
        m = re.match(r"(TaskLog|PRD|Plan|Handover|Handoff|WorkLog)[_\-]", base, re.I)
        if m and not GOOD_NAME.match(base):
            return ("R3 命名不符：「" + base + "」須為「類型_YYYY-MM-DD_主題.md」"
                    "（Handoff／WorkLog 異體已廢，統一 Handover_／TaskLog_）。")
    return None


def check_bash(ti):
    cmd = str(ti.get("command") or "")
    for seg in re.split(r"[;&|\n]+", cmd):
        # R4 禁 git add 全量（lessons 2026-07-02：全量 add 掃進無關未追蹤檔）
        m = re.search(r"\bgit\s+(?:-C\s+\S+\s+)?add\s+(.*)$", seg)
        if m:
            toks = m.group(1).split()
            for t in toks:
                if t == "--":
                    continue
                if t in ("-A", "--all", ".") or t.rstrip("/") == "_context":
                    return ("R4 禁 git add 全量（-A／--all／.／整個 _context）："
                            "只 add 本次確實要提交的具體檔案，避免掃進無關未追蹤檔。")
        # R5 禁 symlink（GLOBAL 鐵律：設定/skills 一律實體複製，跨平台/Drive 必斷）
        if re.search(r"(?:^|\s)ln\s+-\w*s", seg) or re.search(r"\bmklink\b", seg, re.I):
            return ("R5 禁 symlink：設定與 skills 一律實體複製（symlink 跨平台/Drive 必斷，"
                    "GLOBAL.md 鐵律）。確有必要請先向使用者說明並取得核准。")
    return None


def check(tool, ti):
    if tool in WRITE_TOOLS:
        return check_write(tool, ti)
    if tool == "Bash":
        return check_bash(ti)
    return None


def main():
    with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
        data = json.load(f)
    reason = check(data.get("tool_name", ""), data.get("tool_input") or {})
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open：guard 自身錯誤一律放行
    sys.exit(0)
