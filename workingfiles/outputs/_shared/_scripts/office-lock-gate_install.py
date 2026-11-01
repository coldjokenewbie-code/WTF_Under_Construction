#!/usr/bin/env python3
"""把 office-lock-gate 掛進 ~/.claude/settings.json 的 PreToolUse（由三藏親自執行；先備份）。
用法：python3 office-lock-gate_install.py <hook腳本絕對路徑>"""
import json, os, shutil, sys, time
hook = os.path.abspath(sys.argv[1])
assert os.path.isfile(hook), hook
sp = os.path.expanduser('~/.claude/settings.json')
bak = sp + '.' + time.strftime('%Y%m%d-%H%M%S') + '.bak'
shutil.copy2(sp, bak)
cfg = json.load(open(sp))
entry = {"matcher": "Bash|Write|Edit|MultiEdit|NotebookEdit",
         "hooks": [{"type": "command", "command": f"python3 {hook}", "timeout": 20}]}
pre = cfg.setdefault('hooks', {}).setdefault('PreToolUse', [])
if any(hook in h.get('command', '') for e in pre for h in e.get('hooks', [])):
    print('已存在，不重複加入'); sys.exit(0)
pre.append(entry)
json.dump(cfg, open(sp, 'w'), ensure_ascii=False, indent=2)
print('已加入 PreToolUse；備份：', bak)
