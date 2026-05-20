# Antigravity 工具層設定
> 適用：Google Antigravity 專屬
> 來源：WTF_Under_Construction repo — Single Source of Truth（實體路徑：/Users/coma/git_folder/WTF_Under_Construction/claude-config/）
> 載入方式：`~/.gemini/GEMINI.md` 本機存放；`~/.gemini/AGENTS.md` 存放跨工具規則

## Skills 載入

Session 開始時，依序讀取（詳見 `~/.gemini/AGENTS.md` 的 Skills 載入協議）：
1. 全域 skills（UI 自訂路徑：`/Users/coma/git_folder/WTF_Under_Construction/claude-config/skills/`）
2. 專案層 skills（`._agents/skills/` 或 `.claude/skills/`）
3. 若專案有 `_context/`，讀取其中所有 `.md`；若有 `rules/`，讀取其中所有 `.md`


## 溝通用語規範（使用者 vs 業主）

| 稱呼 | 對象 | 說明 |
|---|---|---|
| **使用者／用戶** | 與 AI 對話的人 | 廠商成員，使用 AI 執行受委託工作 |
| **業主** | 委託方（公司或機關） | 採購方，不直接與 AI 互動 |
| **廠商** | 使用者所屬的公司 | 執行業主委託工作的團隊 |

**強制規則：**
- AI 回應中「你」「使用者」一律指**與 AI 對話的人（廠商成員）**，不是業主。
- 「業主提供」「業主確認」「待業主索取」中的**業主**，指委託廠商的客戶端，不是使用者本人。
- 禁止混用。違反此規則視為角色錯誤，需立即更正。

---

## 全域設定存入協議

收到「存入全域設定」指令時：
1. 更新 WTF repo 的 `claude-config/AGENTS.md`（跨工具規則）或 `claude-config/GEMINI.md`（Antigravity 專屬）。
2. 同步更新 `~/.gemini/AGENTS.md` 與 `~/.gemini/GEMINI.md`。
3. 提供本次設定點位摘要。

## 任務通訊協議執行

Antigravity 在完成單一 Composition 或原子任務時，應主動更新 `AGENT_SIGNAL.log`：
- 高效格式：`DONE|<AgentID>|<FileName>|<Timestamp>`
- 此舉旨在觸發 Claude Code 的自動驗收與 Handoff 流程。
