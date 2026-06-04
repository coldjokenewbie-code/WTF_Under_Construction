---
name: session-start
description: Session 開場標準流程：核對全域設定、載入 SSOT、讀取 _context 知識。每次新對話開場執行。
---

# Session Start

每次新對話開場，依序執行下列三步，不需逐步確認；全部完成後回報「已載入全域設定」再詢問任務。

> **前置（自動，無需手動）**：本機 `~/.claude/` 已掛 UserPromptSubmit hook（`wtf-sync.sh`／`wtf-sync.ps1`），在本 session 第一個 prompt 即自動「清 lock → `git pull` → `sync_config.py sync`」（5 分冷卻）。
> 故本 skill **不再無條件 git pull／sync**，只做核對與必要時 fallback，避免與 hook 重工。

## 1. 核對全域設定

0. **定位 SSOT（絕對路徑）**：讀 `~/.claude/wtf-root.txt` 取得本機 WTF repo 絕對路徑 `<WTF_ROOT>`（hook／`sync_config.py` 寫出）。以下一律用 `<WTF_ROOT>` 組**絕對路徑**——`wtf-config` 已移出工作區，**非 WTF 專案用相對 `wtf-config/` 會抓不到**。讀不到 wtf-root.txt → 讀專案本地 `AGENTS.md`（已部署）並回報「SSOT 錨點缺失，請先跑一次 hook 或 sync」。
1. 偵測電腦：本機（Claude Code／終端機）執行
   `python "<WTF_ROOT>/wtf-config/sync_config.py" register`
   （Cowork 沙盒內跳過 `register`，沙盒抓不到實體機名）。
2. 設定檢查：執行
   `python "<WTF_ROOT>/wtf-config/sync_config.py" check`
   - 全 OK（hook 已同步）→ 不需動作。
   - **僅當** check 報 `STALE`／`BROKEN`／`MISSING`（hook 未生效或失敗）→ fallback 執行
     `python "<WTF_ROOT>/wtf-config/sync_config.py" sync` 修復，並回報。
3. 載入 SSOT：讀取 `<WTF_ROOT>/wtf-config/GLOBAL.md` 與 `<WTF_ROOT>/wtf-config/AGENTS.md`。

## 2. 讀取 _context 知識

1. 根知識：讀取 `_context/about-me.md`、`_context/lessons-learned.md`。
2. 進入專案後：讀取該專案 `_context/` 的 PRD 與 `lessons-learned.md`。
   - 工作紀錄依 GLOBAL.md「結案歸檔」規則：只讀 `TaskLog_`／`Handover_`／`INDEX.md`，跳過 `ClosedTaskLog_`／`archive/`。
   - 先看 `INDEX.md` 掌握全貌，再按需展開個別檔案。

## 3. 讀取並套用 rules 規範

讀取 repo 根 `rules/` 全部 `.md`（如 `workingfiles-conventions.md`），套用其規範（檔案存放、命名慣例、輸出格式等）；進入專案後一併讀該專案 `rules/` 全部 `.md`，**專案規範優先於根規範**。

## 完成回報

三步完成後回報「已載入全域設定」，依序帶出：
1. **身分宣告**：`我是 {AI}@{hostname}（{OS}）、repo 在 {path}`。
   - `{AI}`＝本工具類型（Claude／Gemini／Codex，自知）；`{hostname}`／`{OS}`／`{path}` 取自 `register`／`machines.md`／`projects-registry.md` 本機列。
   - 目的：跨機（兩台 Claude）／跨工具協作時，一眼可知「誰在講、哪台、什麼 OS」，避免接手 agent 誤判他人作為己作。
2. 一行 check 狀態（全 OK／已 fallback sync 修復 N 項）。

再詢問本次任務。

> 工作區異常處置：若 `git status` 顯示工作區有未提交變更或無法快轉，**停下通知使用者**，不擅自 merge／rebase／覆蓋（此情境 hook 也會在 pull 失敗時回報）。

> 本 skill 為共用 SSOT，位於 `wtf-config/skills/session-start/`。
> 修改後需各機器執行 `python wtf-config/sync_config.py sync` 重新部署至全域 `~/.claude/skills/`。
