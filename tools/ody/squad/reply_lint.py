#!/usr/bin/env python3
"""ody 輸出守門 linter（Tyrion）。

對一段回覆文字做可機檢規範檢查：禁詞（聊天語氣/浮誇/功勞申報）＋散文字數上限。
違規回傳清單。零依賴。既是 Stop hook 的引擎，也可手動 `echo ... | reply_lint.py` 自評。

學習：每次被使用者糾正，把新違規樣式加進 lint_rules.json 的 banned_phrases，下次自動擋。
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

RULES_PATH = Path(__file__).with_name("lint_rules.json")


def _strip_code_and_tables(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)      # 程式碼區塊
    text = re.sub(r"`[^`]*`", "", text)                    # 行內碼
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("|"))  # 表格列
    return text


def lint(text: str, rules: dict | None = None) -> list[str]:
    if rules is None:
        rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    v = []
    for p in rules.get("banned_phrases", {}).get("list", []):
        if p in text:
            v.append(f"禁詞: {p!r}（聊天語氣/浮誇/功勞——刪除）")
    prose = _strip_code_and_tables(text)
    prose_len = len(re.sub(r"\s", "", prose))
    limit = rules.get("max_prose_chars", {}).get("limit", 0)
    if limit and prose_len > limit:
        v.append(f"過長: 散文 {prose_len} 字 > 上限 {limit}（結論先行、砍贅述）")
    return v


def main() -> int:
    text = sys.stdin.read()
    v = lint(text)
    if v:
        print("【ody-lint 違規】", file=sys.stderr)
        for x in v:
            print(" - " + x, file=sys.stderr)
        return 1
    print("ok", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
