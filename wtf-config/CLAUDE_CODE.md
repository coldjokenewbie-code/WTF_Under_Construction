# Claude Code 工具層設定

> **應用範疇**：Claude Code CLI / IDE Extension / Web(remote) 專屬。
> **載入方式**：`sync_config.py` 部署本檔為 `~/.claude/CLAUDE.md`，Claude Code 原生自動載入。
> **定位**：只放初始化入口與 Claude Code 專屬差異；全域設定＝`GLOBAL.md`＋`AGENTS.md` 兩檔（通則與規範、溝通與角色），本檔不重複其內容。

## 強制初始化協議（對話開始時立即執行，不得跳過）

0. **定位 SSOT（絕對路徑）**：讀 `~/.claude/wtf-root.txt` 取得本機 WTF repo 絕對路徑 `<WTF_ROOT>`（由 hook／`sync_config.py` 寫出，不可用相對路徑）。讀不到時：改讀專案本地 `AGENTS.md`（sync 已部署），並回報「SSOT 錨點缺失，請先跑一次 hook 或 `sync_config.py sync`」。
1. **讀取全域設定兩檔**：`<WTF_ROOT>/wtf-config/GLOBAL.md` 與 `<WTF_ROOT>/wtf-config/AGENTS.md`，並依 GLOBAL.md「開場協議」執行（含專案知識三檔制）。SessionStart hook 若已注入兩檔內容且無截斷提示，可視為已讀；**凡出現「Output too large／Preview」等截斷字樣，必須立即完整 Read 原檔，不得以預覽或關鍵字搜尋代替**。
2. 向用戶說明「已載入全域與 CLAUDE_CODE 工具設定」，僅首次啟動報告一次。

## Claude Code 專屬差異

- **派工**：subagent 用 Agent tool 派（`model` 參數顯式指定）；驗證派 fresh-context subagent，不自驗。派工前先過 GLOBAL.md「派工鐵律」，選 model 時開 `<WTF_ROOT>/wtf-config/playbooks/model-dispatch.md`。
- **新專案（無 `.claude/` 設定）**：列出可用 skills（lazy，不讀 body）→ 簡述啟用項 → 詢問任務或目標。
- **現有專案**：全域 skills 原生自動列；專案 skills 照 AGENTS.md「Skills 載入協議」主動列 `._agents/skills/`。簡述啟用規則（例：`[Dev_Workflow 啟用中]`）後詢問任務。
- **任務通訊**：照 AGENTS.md「任務通訊協議」，AgentID 用 `Claude`。

## Claude Code 專屬按需檔（情境到才開）

| 情境 | 開啟 `<WTF_ROOT>/wtf-config/playbooks/` |
|---|---|
| 同 repo 多個 CLI 並行、監聽 log | `parallel-worktree.md` |
| ui-review／前端手勢／資產路徑 | `pitfalls-frontend.md` |
| pptx／docx／gen 腳本 | `pitfalls-office-docs.md` |
