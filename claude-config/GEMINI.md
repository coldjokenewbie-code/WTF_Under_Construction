# Antigravity Agent Rules
> 適用：Google Antigravity 專屬
> 基礎規則見 ~/.gemini/AGENTS.md，本檔為 Antigravity 專屬補充

## Skills 載入

session 開始時：
1. 讀取 `~/.gemini/antigravity/global_skills/`，確認可用 skills。
2. 讀取 `~/.gemini/skills/`（全域 skills）。
3. 簡述啟用中的 skills。

## 工具層級設定

Antigravity 專屬慣例獨立存放：
- 跨工具通用規則：`~/.gemini/AGENTS.md`
- Antigravity 專屬：`~/.gemini/GEMINI.md`（本檔）

## 全域設定存入協議

收到「存入全域設定」指令時：
1. 更新 WTF_Under_Construction repo 的 `claude-config/AGENTS.md`（跨工具規則）或 `claude-config/GEMINI.md`（Antigravity 專屬）。
2. 提供本次設定點位摘要。
