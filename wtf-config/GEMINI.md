# Antigravity 工具層設定

> **應用範疇**：Google Antigravity 專屬。
> **載入方式**：本檔由 `sync_config.py sync` **實體複製**到 `~/.gemini/GEMINI.md`（Antigravity 原生開場讀 `GEMINI.md`）。不用 symlink（跨平台/搬遷會斷鏈）；`~/.gemini/AGENTS.md` 已棄用，靠本檔 bootstrap 讀 repo 內正本。
> **定位**：只放初始化入口與 Antigravity 專屬差異；全域設定＝`GLOBAL.md`＋`AGENTS.md` 兩檔（通則與規範、溝通與角色），本檔不重複其內容。

## 強制初始化協議（對話開始時立即執行，不得跳過）

0. **定位 SSOT（絕對路徑）**：讀 `~/.gemini/wtf-root.txt`（或 `~/.claude/wtf-root.txt`）取得本機 WTF repo 絕對路徑 `<WTF_ROOT>`。`wtf-config` 已移出工作區，不可用相對路徑。
1. **讀取全域設定兩檔**：以 `view_file` 讀 `<WTF_ROOT>/wtf-config/GLOBAL.md` 與 `<WTF_ROOT>/wtf-config/AGENTS.md`，並依 GLOBAL.md「開場協議」執行（含專案知識三檔制）、依 AGENTS.md 執行 Skills 載入協議。
2. **同步檢查**：在本地終端機執行 `python "<WTF_ROOT>/wtf-config/sync_config.py" check`，確認設定與真相源一致。
3. **初始化回報與身分宣告**（僅 session 首次對話一次，後續不重複）：以「已載入全域與 GEMINI 工具設定」開頭，依序帶出：
   - `我是 Antigravity@{hostname}（{OS}）、repo 在 {path}`
   - `全域同步檢查狀態：[check 輸出狀態]`
   - `目前可用技能：[列出與本案相關的 skills 名稱，不讀 body]`

## Antigravity 專屬差異

- **全域 skills 位置**：真相源 `wtf-config/skills/` 由 sync 實體複製到 `~/.gemini/skills/`（保留工具自有 skill）；載入規則照 AGENTS.md「Skills 載入協議」。
- **監控指令檔**：若專案有 `_context/MONITOR_INSTRUCTION_gemini.md`：a) 先讀「現在的待處理請求」欄位，有待辦立即執行，不等 tail 觸發；b) 在背景執行檔中的監控指令（`tail -n 0 -f ... | grep ...`），讓後續 REQUEST 信號自動觸發；執行新任務後繼續保持監控。
- **定時喚醒防卡死**：背景監控（如 tail 監聽 `AGENT_SIGNAL.log`）必須配合 `schedule` 啟動定時器（例如 90 秒，`TimerCondition` 依情境設定），定時喚醒自己主動檢查監控腳本狀態與日誌更新；禁止被動等待喚醒，避免 AI 進入 idle 後監控中斷。
- **任務通訊**：照 AGENTS.md「任務通訊協議」，AgentID 用 `Antigravity`。
- **存入全域設定**：照 GLOBAL.md「存入協議」；本工具專屬檔＝`wtf-config/GEMINI.md`。
