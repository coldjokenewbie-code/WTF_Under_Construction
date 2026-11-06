#!/usr/bin/env python3
"""安裝 w-colab-gate：複製 hook 到 repo 的 hook 資料夾，並登記到使用者設定的 PreToolUse（先備份）。
由 PO 親自執行、不帶參數：python3 workingfiles/outputs/_shared/_scripts/w-colab-gate_install.py"""
import json
import os
import shutil
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
root = here
for _ in range(4):
    root = os.path.dirname(root)
src = os.path.join(here, 'w-colab-gate.py')
dst_dir = os.path.join(root, 'wtf-config', 'hooks')
dst = os.path.join(dst_dir, 'w-colab-gate.py')
assert os.path.isfile(src), src
os.makedirs(dst_dir, exist_ok=True)
shutil.copy2(src, dst)
print('已複製 hook：', dst)

sp = os.path.join(os.path.expanduser('~'), '.claude', 'settings.json')
cfg = json.load(open(sp, encoding='utf-8'))
cmd = 'python3 ' + dst
pre = cfg.setdefault('hooks', {}).setdefault('PreToolUse', [])
if any(h.get('command') == cmd for e in pre for h in e.get('hooks', [])):
    print('設定已登記同一 command，不重複加入（只更新了 hook 檔）')
    sys.exit(0)
bak = sp + '.' + time.strftime('%Y%m%d-%H%M%S') + '.bak'
shutil.copy2(sp, bak)
pre.append({"matcher": "Bash|Write|Edit|MultiEdit|NotebookEdit",
            "hooks": [{"type": "command", "command": cmd, "timeout": 20}]})
with open(sp, 'w', encoding='utf-8') as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)
print('已加入 PreToolUse：', cmd)
print('設定備份：', bak)
