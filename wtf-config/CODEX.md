# Codex 工具層設定

> **應用範疇**：OpenAI Codex 專屬。
> **載入方式**：本檔由 `sync_config.py sync` **實體複製**到 `~/.codex/AGENTS.md`（Codex 原生開場讀 `AGENTS.md`，不讀 `CODEX.md`；實測 `codex debug prompt-input` 確認）。不用 symlink（跨平台/搬遷會斷鏈）。
> **定位**：只放初始化入口與 Codex 專屬差異；全域設定＝`GLOBAL.md`＋`AGENTS.md` 兩檔（通則與規範、溝通與角色），本檔不重複其內容。

## 強制初始化協議（對話開始時立即執行，不得跳過）

0. **定位 SSOT（絕對路徑）**：讀 `~/.codex/wtf-root.txt`（或 `~/.claude/wtf-root.txt`）取得本機 WTF repo 絕對路徑 `<WTF_ROOT>`。`wtf-config` 已移出工作區，不可用相對路徑。
1. **讀取全域設定兩檔**：以 `view_file` 讀 `<WTF_ROOT>/wtf-config/GLOBAL.md` 與 `<WTF_ROOT>/wtf-config/AGENTS.md`，並依 GLOBAL.md「開場協議」執行（含專案知識三檔制）、依 AGENTS.md 執行 Skills 載入協議。
2. 向用戶說明「已載入全域與 CODEX 工具設定」再開始工作（僅 session 首次一次，後續不重複）。

## Codex 專屬差異

- **全域 skills 位置**：真相源 `wtf-config/skills/` 由 sync 實體複製到 `~/.codex/skills/`（保留工具自有 skill 如 find-skills）；載入規則照 AGENTS.md「Skills 載入協議」。
- **監控指令檔**：若專案有 `_context/MONITOR_INSTRUCTION_codex.md`：a) 先讀「現在的待處理請求」欄位，有待辦立即執行，不等 tail 觸發；b) 在背景執行檔中的監控指令（`tail -n 0 -f ... | grep ...`），讓後續 REQUEST 信號自動觸發；執行新任務後繼續保持監控。
- **工具呼叫權限慣例**：需要重複呼叫外部服務或會觸發 sandbox escalation 的流程（Vertex AI 生圖、gcloud、網路生成工具），先固定成同一個 wrapper 腳本或固定命令前綴再批次執行；不要每次臨時換 prompt 檔/輸出檔組成不同命令，否則 Codex 會把每條視為不同前綴而反覆要求授權。
- **任務通訊**：照 AGENTS.md「任務通訊協議」，AgentID 用 `Codex`。
- **存入全域設定**：照 GLOBAL.md「存入協議」；本工具專屬檔＝`wtf-config/CODEX.md`。
