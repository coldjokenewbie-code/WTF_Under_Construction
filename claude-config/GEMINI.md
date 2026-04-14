# Antigravity 工具層設定
> 適用：Google Antigravity 專屬
> 載入方式：`~/.gemini/GEMINI.md` 本機存放；`~/.gemini/AGENTS.md` 存放跨工具規則

## Skills 載入

Session 開始時，依序讀取（詳見 `~/.gemini/AGENTS.md` 的 Skills 載入協議）：
1. 全域 skills（UI 自訂路徑：`WTF_Under_Construction/claude-config/skills/`）
2. 專案層 skills（`._agents/skills/` 或 `.claude/skills/`）

## 全域設定存入協議

收到「存入全域設定」指令時：
1. 更新 WTF repo 的 `claude-config/AGENTS.md`（跨工具規則）或 `claude-config/GEMINI.md`（Antigravity 專屬）。
2. 同步更新 `~/.gemini/AGENTS.md` 與 `~/.gemini/GEMINI.md`。
3. 提供本次設定點位摘要。
