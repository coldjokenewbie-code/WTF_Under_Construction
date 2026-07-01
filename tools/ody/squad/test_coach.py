#!/usr/bin/env python3
"""coach.py 自測（離線、零依賴）。python3 tools/ody/squad/test_coach.py"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coach  # noqa: E402

FAILS = []


def check(name: str, cond: bool, detail: str = ""):
    print(("v " if cond else "x ") + name + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


# _match：fnmatch 的 * 可跨 /；/** 為前綴制
check("match 一般 glob", coach._match("tools/ody/squad/coach.py", ["tools/ody/squad/*"]))
check("match /** 前綴", coach._match("tools/ody/data/contracts/x.json", ["tools/ody/data/**"]))
check("match 不誤放", not coach._match("wtf-config/GLOBAL.md", ["tools/ody/squad/*"]))

# R001 保護路徑：未明授→擋；--po-authorized→放
f1: list[str] = []
coach._apply_rules({"po_authorized_protected_paths": False, "acceptance": []},
                   [".claude/settings.local.json"], f1)
check("R001 未明授擋保護路徑", any("R001" in x for x in f1), str(f1))
f2: list[str] = []
coach._apply_rules({"po_authorized_protected_paths": True, "acceptance": []},
                   [".claude/settings.local.json"], f2)
check("R001 明授放行", not any("R001" in x for x in f2), str(f2))

# R002 證據空話：note='已確認'→擋；具體 note→放
f3: list[str] = []
coach._apply_rules({"po_authorized_protected_paths": False,
                    "acceptance": [{"no": 1, "evidence": {"note": "已確認"}}]}, [], f3)
check("R002 擋空話證據", any("R002" in x for x in f3), str(f3))
f4: list[str] = []
coach._apply_rules({"po_authorized_protected_paths": False,
                    "acceptance": [{"no": 1, "evidence": {"note": "diff 見 x.py:12 新增守門"}}]},
                   [], f4)
check("R002 具體 note 放行", not f4, str(f4))

# _dirty_files 解析回歸：porcelain 首行前導空白曾被 strip 吃掉致路徑掉首字
for p in coach._dirty_files():
    if not (coach.WTF_ROOT / p).exists():
        check("dirty 路徑存在（porcelain 解析回歸）", False, p)
        break
else:
    check("dirty 路徑存在（porcelain 解析回歸）", True)

if FAILS:
    print(f"\nFAIL {len(FAILS)} 項：{FAILS}", file=sys.stderr)
    sys.exit(1)
print("\n全部通過")
