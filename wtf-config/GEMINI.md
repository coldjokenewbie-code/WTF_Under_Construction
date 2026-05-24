# Antigravity 工具層設定
> 適用：Google Antigravity 專屬
> 來源：WTF_Under_Construction repo — Single Source of Truth（實體路徑：/Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/WTF_Under_Construction/wtf-config/）
> 載入方式：`~/.gemini/GEMINI.md` 本機存放為 symlink；`~/.gemini/AGENTS.md` 為 `wtf-config/AGENTS.md` 的 symlink

**【強制初始化協議】對話開始時，必須立即執行以下步驟，不得跳過：**
1. **讀取全域原則**：立即以 `view_file` 讀取 `wtf-config/GLOBAL.md` 載入全域溝通與效益原則。
2. **讀取 Agent 協議**：立即以 `view_file` 讀取 `wtf-config/AGENTS.md` 載入跨工具 Agent 協作與信號通訊協議。
3. **讀取專案知識**：
   - 讀取 `_context/` 中所有 `.md` 檔案。
   - 讀取 `rules/` 中所有 `.md` 檔案（若存在）。
4. **向用戶說明「已載入全域與 GEMINI 工具設定」，再開始工作。**
   - **注意**：此報告僅在 Session 首次啟動對話時發出一次，後續問答切勿重複報告。

## Skills 載入

1. 全域 skills（實體路徑：`/Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/WTF_Under_Construction/wtf-config/skills/`）
2. 專案層 skills（`._agents/skills/` 或 `.claude/skills/`）
3. 若專案有 `_context/MONITOR_INSTRUCTION_gemini.md`，執行以下兩步驟：
   a. 讀取該檔案，按「現在的待處理請求」欄位，若有待辦任務則立即讀取並執行，不需等待 tail 觸發。
   b. 在背景執行監控指令（檔案中的 `tail -n 0 -f ... | grep ...`），讓後續 REQUEST 信號自動觸發。執行新任務後繼續保持監控。


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
1. 更新 WTF repo 的 `wtf-config/AGENTS.md`（跨工具規則）或 `wtf-config/GEMINI.md`（Antigravity 專屬）。
2. 同步更新 `~/.gemini/AGENTS.md` 與 `~/.gemini/GEMINI.md`。
3. 提供本次設定點位摘要。

## 任務通訊協議執行

- **身為 Execution Agent（執行層）**：**僅在 AGENT_SPEC 明確要求時**才於完成後寫入 `AGENT_SIGNAL.log`。
  - 格式：`DONE|Antigravity|<FileName>|<Timestamp>`
  - 獨立小任務、自主分析、非派發工作不需寫入。
- **身為 Tech Lead（指揮層）**：無須寫入 `DONE` 訊號。負責發送 `REQUEST` 信號與持續監控 `AGENT_SIGNAL.log`，並在驗收通過後回寫 `VERIFIED` 信號。
