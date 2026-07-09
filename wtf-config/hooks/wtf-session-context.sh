#!/bin/bash
# wtf-session-context.sh — SessionStart hook：把 GLOBAL.md/AGENTS.md + 三檔制內容直接注入 context
# 設計原則：不提醒模型去讀（那靠自律），直接灌內容（不需遵從）。
# 部署：複製到 ~/.claude/ 並 chmod +x；註冊見檔尾。cwd＝專案根目錄（Claude Code hook 預設）。
# 正本：WTF repo wtf-config/hooks/（黃區，改動走 maintenance-protocol）

d="_context"
[ -d "$d" ] || exit 0   # 無 _context 的目錄（非專案）安靜跳過

CAP=150   # 每檔注入上限行數，控 token 成本

echo "【開場注入｜GLOBAL.md/AGENTS.md + 三檔制內容已由 SessionStart hook 自動載入，無需再讀這些檔】"

# GLOBAL.md／AGENTS.md：在專案外（wtf-config/），走 WTF_ROOT 錨點定位（機制見 GLOBAL.md 檔頭）
root_file="$HOME/.claude/wtf-root.txt"
WTF_ROOT=""
[ -f "$root_file" ] && WTF_ROOT=$(cat "$root_file")

if [ -n "$WTF_ROOT" ]; then
  for f in "$WTF_ROOT/wtf-config/GLOBAL.md" "$WTF_ROOT/wtf-config/AGENTS.md"; do
    if [ -f "$f" ]; then
      echo "===== $f ====="
      head -n "$CAP" "$f"
      [ "$(wc -l < "$f")" -gt "$CAP" ] && echo "……（超過 ${CAP} 行已截斷，需完整內容再讀原檔）"
    fi
  done
else
  echo "【警告：~/.claude/wtf-root.txt 缺失，GLOBAL.md/AGENTS.md 未能注入，需自行讀取】"
fi

for f in "$d/INDEX.md" "$d/lessons-learned.md"; do
  if [ -f "$f" ]; then
    echo "===== $f ====="
    head -n "$CAP" "$f"
    [ "$(wc -l < "$f")" -gt "$CAP" ] && echo "……（超過 ${CAP} 行已截斷，需完整內容再讀原檔）"
  fi
done

# 當前 TaskLog：取檔名日期最新一份（命名慣例 TaskLog_YYYY-MM-DD_主題.md，字典序＝日期序）
tl=$(ls -1 "$d"/TaskLog_*.md 2>/dev/null | sort | tail -1)
if [ -n "$tl" ]; then
  echo "===== 當前 TaskLog：$tl ====="
  head -n "$CAP" "$tl"
  [ "$(wc -l < "$tl")" -gt "$CAP" ] && echo "……（截斷，需完整內容再讀原檔）"
fi

echo "【注入結束。其他 _context/ 檔案只在上方 INDEX 讀取指引點名或使用者點名時才讀；嚴禁全量掃描。動手前過 GLOBAL.md「制度層」派工鐵律。】"

# 註冊（~/.claude/settings.json 的 hooks 段；Windows 預設 Git Bash 可直接用 bash 執行）：
# "SessionStart": [{"hooks": [{"type": "command", "command": "bash ~/.claude/wtf-session-context.sh"}]}]
