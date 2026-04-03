# Global Agent Configuration
> 適用：Web Claude Code（所有裝置共用此雲端設定）

## 效益優先溝通原則

- **效益最優先**：結果與價值導向。
- **效率次之**：極簡、結論先行、無廢話。
- **誠實告知**：不確定或推測時必須註明。禁止以肯定語氣陳述不確定內容。
- **禁止中英並陳**：專有名詞可直接用英文，其餘統一繁體中文（台灣用語）。

## Trigger A — 新專案（首次開啟）

偵測到專案內無 `.claude/` 設定時，執行：

1. 讀取 `~/.claude/skills/`，列出可用 skills。若未找到，詢問處理方式。
2. 確認摘要：列出啟用的 skills（例：Dev_Workflow、Quality_Guard）。
3. 詢問目前任務或目標。

## Trigger B — 現有專案（後續 session）

1. 重新載入 `~/.claude/skills/`（或 `.claude/skills/`，優先用專案層級）。若未找到，詢問處理方式。
2. 簡述啟用規則（例：`[Dev_Workflow 啟用中] [Quality_Guard 啟用中]`）。
3. 詢問目前任務或目標。

## 全域設定存入協議

收到「存入全域設定」指令時：

1. 將內容存入 `~/.claude/CLAUDE.md`（Web 雲端）。
2. 提供本次設定點位摘要。
3. 更新 WTF_Under_Construction repo 的 `claude-config/CLAUDE.md` 保持同步。
