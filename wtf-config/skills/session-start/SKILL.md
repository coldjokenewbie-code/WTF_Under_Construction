---
name: session-start
description: Session 開場標準流程：核對全域設定、載入 SSOT、讀取 _context 知識。每次新對話開場執行。
---

# Session Start

每次新對話開場，依序執行下列三步，不需逐步確認；全部完成後回報「已載入全域設定」再詢問任務。

> **前置（自動，無需手動）**：本機 `~/.claude/` 已掛 UserPromptSubmit hook（`wtf-sync.sh`／`wtf-sync.ps1`），在本 session 第一個 prompt 即自動「清 lock → `git pull` → `sync_config.py sync`」（5 分冷卻）。
> 故本 skill **不再無條件 git pull／sync**，只做核對與必要時 fallback，避免與 hook 重工。

## 1. 核對全域設定

> **python 指令依平台選（毋須試錯）**：環境 block 的 `Platform` 已標明 OS——macOS／Linux（darwin/linux）用 `python3`，Windows（win32）用 `python`。下文 `<PY>` 即代表此指令；別固定寫死，否則 Mac 上 `python` 不存在會報 `command not found`。

0. **定位 SSOT（絕對路徑）**：讀 `~/.claude/wtf-root.txt` 取得本機 WTF repo 絕對路徑 `<WTF_ROOT>`（hook／`sync_config.py` 寫出）。以下一律用 `<WTF_ROOT>` 組**絕對路徑**——`wtf-config` 已移出工作區，**非 WTF 專案用相對 `wtf-config/` 會抓不到**。讀不到 wtf-root.txt → 讀專案本地 `AGENTS.md`（已部署）並回報「SSOT 錨點缺失，請先跑一次 hook 或 sync」。
1. 偵測電腦：本機（Claude Code／終端機）執行
   `<PY> "<WTF_ROOT>/wtf-config/sync_config.py" register`
   （Cowork 沙盒內跳過 `register`，沙盒抓不到實體機名）。
2. 設定檢查：執行
   `<PY> "<WTF_ROOT>/wtf-config/sync_config.py" check`
   - 全 OK（hook 已同步）→ 不需動作。
   - **僅當** check 報 `STALE`／`BROKEN`／`MISSING`（hook 未生效或失敗）→ fallback 執行
     `<PY> "<WTF_ROOT>/wtf-config/sync_config.py" sync` 修復，並回報。
3. 載入 SSOT：讀取 `<WTF_ROOT>/wtf-config/GLOBAL.md` 與 `<WTF_ROOT>/wtf-config/AGENTS.md`。
4. **全域設定修改建議**：讀 `<WTF_ROOT>/_context/nightly-notify.md`（不存在則略過）。若有**未勾 `- [ ]`** 項 → 開場**優先醒目提醒**：「💡 nightly 建議修改全域設定：<列出>，要採用嗎？採用我幫你套用並移除該行，不採用就刪行。」夜間 routine **只建議不自改**全域設定，由用戶在此核准（routine 寫建議→commit main→本機 pull→此處浮出）。

## 2. 讀取 _context 知識（三檔制，嚴禁全量掃描）

與 GLOBAL.md 開場協議第 3 步同文，對當前工作目錄（根層或專案層皆同）：
1. 讀 `_context/INDEX.md`（現況與指路）。
2. 讀 INDEX 指到的**當前 TaskLog 一份**（todo 真相源）。
3. 讀 `_context/lessons-learned.md`（若存在，永遠讀）。
4. 其他 `_context/` 檔案（PRD、Handover、其他 TaskLog）**只在** INDEX「讀取指引」點名、或使用者點名時才讀；`archive/`／`ClosedTaskLog_*` 一律跳過。

## 3. 讀取並套用 rules 規範

讀取 repo 根 `rules/` 全部 `.md`（如 `folder-conventions.md`），套用其規範（檔案存放、命名慣例、輸出格式等）；進入專案後一併讀該專案 `rules/` 全部 `.md`，**專案規範優先於根規範**。

## 完成回報

三步完成後回報「已載入全域設定」，依序帶出：
1. **身分宣告**：`我是 {AI}@{hostname}（{OS}）、repo 在 {path}`。
   - `{AI}`＝本工具類型（Claude／Gemini／Codex，自知）；`{hostname}`／`{OS}`／`{path}` 取自 `register`／`machines.md`／`projects-registry.md` 本機列。
   - 目的：跨機（兩台 Claude）／跨工具協作時，一眼可知「誰在講、哪台、什麼 OS」，避免接手 agent 誤判他人作為己作。
2. 一行 check 狀態（全 OK／已 fallback sync 修復 N 項）。

再詢問本次任務。

> 工作區異常處置：若 `git status` 顯示工作區有未提交變更或無法快轉，**停下通知使用者**，不擅自 merge／rebase／覆蓋（此情境 hook 也會在 pull 失敗時回報）。

> 本 skill 為共用 SSOT，位於 `wtf-config/skills/session-start/`。
> 修改後需各機器執行 `<PY> wtf-config/sync_config.py sync`（`<PY>`：Mac/Linux=`python3`、Windows=`python`）重新部署至全域 `~/.claude/skills/`。
