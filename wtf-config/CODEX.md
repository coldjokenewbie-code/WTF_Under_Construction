# Codex 工具層設定
> 適用：OpenAI Codex 專屬
> 來源：WTF_Under_Construction repo — Single Source of Truth（git repo，已移出雲端硬碟；各機實體路徑見 wtf-config/projects-registry.md）
> 載入方式：`~/.codex/CODEX.md` 本機存放為 symlink；`~/.gemini/AGENTS.md` 為 `wtf-config/AGENTS.md` 的 symlink

**【強制初始化協議】對話開始時，必須立即執行以下步驟，不得跳過：**
1. **讀取全域原則**：立即以 `view_file` 讀取 `wtf-config/GLOBAL.md` 載入全域溝通與效益原則。
2. **讀取 Agent 協議**：立即以 `view_file` 讀取 `wtf-config/AGENTS.md` 載入跨工具 Agent 協作與信號通訊協議。
3. **讀取專案知識**：
   - 讀取 `_context/` 中所有 `.md` 檔案。
   - 讀取 `rules/` 中所有 `.md` 檔案（若存在）。
4. **向用戶說明「已載入全域與 CODEX 工具設定」，再開始工作。**
   - **注意**：此報告僅在 Session 首次啟動對話時發出一次，後續問答切勿重複報告。

## Session 開始時執行

1. 執行 `~/.codex/sync-skills.sh` — 自動將 WTF repo 新增的 skills symlink 到 `~/.codex/skills/`
2. 依序讀取：
   - 全域 skills（真相源 `wtf-config/skills/`）
   - 專案層 skills（`._agents/skills/` 或 `.claude/skills/`）
3. 若專案有 `_context/MONITOR_INSTRUCTION_codex.md`，執行以下兩步驟：
   a. 讀取該檔案，按「現在的待處理請求」欄位，若有待辦任務則立即讀取並執行，不需等待 tail 觸發。
   b. 在背景執行監控指令（檔案中的 `tail -n 0 -f ... | grep ...`），讓後續 REQUEST 信號自動觸發。執行新任務後繼續保持監控。

## 任務通訊協議執行

- **身為 Execution Agent（執行層）**：**僅在 AGENT_SPEC 明確要求時**才於完成後寫入 `AGENT_SIGNAL.log`。
  - 格式：`DONE|Codex|<FileName>|<Timestamp>`
  - 獨立小任務、自主分析、非派發工作不需寫入。
- **身為 Tech Lead（指揮層）**：無須寫入 `DONE` 訊號。負責發送 `REQUEST` 信號與持續監控 `AGENT_SIGNAL.log`，並在驗收通過後回寫 `VERIFIED` 信號。

## 全域設定存入協議

收到「存入全域設定」指令時：
1. 更新 WTF repo 的 `wtf-config/CODEX.md`（Codex 專屬）或 `wtf-config/AGENTS.md`（跨工具規則）。
2. `~/.codex/CODEX.md` 為 symlink，自動同步，無需手動複製。
3. 提供本次設定點位摘要。
