#!/bin/bash
# wtf-pretooluse-guard.sh — PreToolUse hook 入口：落地 stdin JSON 後交給規則引擎（同名 .py）。
# fail-open：任何一步失敗都 exit 0 放行。規則本體與設計說明見 wtf-pretooluse-guard.py。
# 正本：WTF repo wtf-config/hooks/（黃區，改動走 maintenance-protocol）。

PY=$(command -v python3 || command -v python) || exit 0
tmp=$(mktemp 2>/dev/null) || exit 0
cat > "$tmp" 2>/dev/null
"$PY" "$HOME/.claude/wtf-pretooluse-guard.py" "$tmp" 2>/dev/null
rm -f "$tmp"
exit 0

# 部署：sync_config.py sync 會把 hooks/ 內容複製到 ~/.claude/。
# 註冊（~/.claude/settings.json 的 hooks 段；加入後需開新 session 才生效，hook 不熱載）：
# "PreToolUse": [{"matcher": "Write|Edit|MultiEdit|NotebookEdit|Bash",
#                 "hooks": [{"type": "command", "command": "bash ~/.claude/wtf-pretooluse-guard.sh"}]}]
