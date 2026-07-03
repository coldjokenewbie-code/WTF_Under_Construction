# Claude Code 工具層設定
> 適用：Claude Code CLI / IDE Extension / Web(remote)
> 載入方式：`sync_config.py` 部署本檔為 `~/.claude/CLAUDE.md`，本機自動載入
> 本檔＝入口索引：只放初始化協議與 Claude Code 專屬差異；通則在 GLOBAL.md，長內容在 playbooks（2026-07-03 重構，舊版在 `wtf-config/archive/2026-07-03_pre-fable5/`）

**【強制初始化協議】對話開始時，必須立即執行以下步驟，不得跳過：**
0. **定位 SSOT（絕對路徑）**：讀 `~/.claude/wtf-root.txt` 取得本機 WTF repo 絕對路徑 `<WTF_ROOT>`（此檔由 hook／`sync_config.py` 寫出，**不可用相對路徑**）。讀不到時 fallback：讀專案本地 `AGENTS.md`（sync 已部署），並回報「SSOT 錨點缺失，請先跑一次 hook 或 `sync_config.py sync`」。
1. **讀取全域原則**：讀 `<WTF_ROOT>/wtf-config/GLOBAL.md`（含開場協議、制度層路由、檔案規範）。
2. **讀取 Agent 協議**：讀 `<WTF_ROOT>/wtf-config/AGENTS.md`（溝通原則與角色定義的正本）。
3. **讀取專案知識——照 GLOBAL.md 開場協議第 3 步的「三檔制」**：INDEX.md → 當前 TaskLog 一份 → lessons-learned.md；`rules/` 全讀；其餘按 INDEX 指路，嚴禁全量掃描 `_context/`。
4. 向用戶說明「已載入全域與 CLAUDE_CODE 工具設定」，僅首次啟動報告一次。

## 動手前（每個任務）

- 先過 GLOBAL.md「制度層：派工鐵律」三條；要派工或選 model 時開 `<WTF_ROOT>/wtf-config/playbooks/model-dispatch.md`。
- Claude Code 專屬：subagent 用 Agent tool 派（`model` 參數顯式指定）；驗證派 fresh-context subagent，不自驗。

## Trigger A — 新專案（首次開啟）

偵測到專案內無 `.claude/` 設定時：列出 `~/.claude/skills/` 可用 skills（lazy，不讀 body）→ 簡述啟用項 → 詢問目前任務或目標。

## Trigger B — 現有專案（後續 session）

1. 全域 skills 原生自動列；**專案 skill 一律放專案內 `._agents/skills/`**——原生清單不含此目錄，進專案時主動列其 SKILL.md 名稱＋描述（lazy），同名時專案版優先。
2. 簡述啟用規則（例：`[Dev_Workflow 啟用中]`），詢問目前任務或目標。

## 任務通訊協議執行

- **身為 Execution Agent（執行層）**：僅在 AGENT_SPEC 明確要求時才於完成後寫入 `AGENT_SIGNAL.log`，格式 `DONE|Claude|<FileName>|<Timestamp>`。獨立小任務不寫。
- **身為 Tech Lead（指揮層）**：不寫 `DONE`；負責發 `REQUEST`、監控 `AGENT_SIGNAL.log`、驗收後回寫 `VERIFIED`。

## Claude Code 專屬按需檔（情境到才開）

| 情境 | 開啟 `<WTF_ROOT>/wtf-config/playbooks/` |
|---|---|
| 同 repo 多個 CLI 並行、監聽 log | `parallel-worktree.md` |
| ui-review／前端手勢／資產路徑 | `pitfalls-frontend.md` |
| pptx／docx／gen 腳本 | `pitfalls-office-docs.md` |
