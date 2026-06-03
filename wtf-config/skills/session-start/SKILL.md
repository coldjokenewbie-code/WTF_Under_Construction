---
name: session-start
description: Session 開場標準流程：核對全域設定、載入 SSOT、讀取 _context 知識。每次新對話開場執行。
---

# Session Start

每次新對話開場，依序執行下列三步，不需逐步確認；全部完成後回報「已載入全域設定」再詢問任務。

> **前置（自動，無需手動）**：本機 `~/.claude/` 已掛 UserPromptSubmit hook（`wtf-sync.sh`／`wtf-sync.ps1`），在本 session 第一個 prompt 即自動「清 lock → `git pull` → `sync_config.py sync`」（5 分冷卻）。
> 故本 skill **不再無條件 git pull／sync**，只做核對與必要時 fallback，避免與 hook 重工。

## 1. 核對全域設定

1. 偵測電腦：本機（Claude Code／終端機）執行
   `python wtf-config/sync_config.py register`
   （Cowork 沙盒內跳過 `register`，沙盒抓不到實體機名）。
2. 設定檢查：執行
   `python wtf-config/sync_config.py check`
   - 全 OK（hook 已同步）→ 不需動作。
   - **僅當** check 報 `STALE`／`BROKEN`／`MISSING`（hook 未生效或失敗）→ fallback 執行
     `python wtf-config/sync_config.py sync` 修復，並回報。
3. 載入 SSOT：讀取 `wtf-config/GLOBAL.md` 與 `wtf-config/AGENTS.md`。

## 2. 讀取 _context 知識

1. 根知識：讀取 `_context/about-me.md`、`_context/lessons-learned.md`、`_context/rules/` 全部 `.md`。
2. 進入專案後：讀取該專案 `_context/` 的 PRD 與 `lessons-learned.md`、`rules/` 全部 `.md`。
   - 工作紀錄依 `tasklog-naming` 規則：只讀 `TaskLog_`／`Handover_`／`INDEX.md`，跳過 `ClosedTaskLog_`。
   - 先看 `INDEX.md` 掌握全貌，再按需展開個別檔案。

## 完成回報

兩步完成後回報「已載入全域設定」，附一行 check 狀態（全 OK／已 fallback sync 修復 N 項），再詢問本次任務。

> 工作區異常處置：若 `git status` 顯示工作區有未提交變更或無法快轉，**停下通知使用者**，不擅自 merge／rebase／覆蓋（此情境 hook 也會在 pull 失敗時回報）。

> 本 skill 為共用 SSOT，位於 `wtf-config/skills/session-start/`。
> 修改後需各機器執行 `python wtf-config/sync_config.py sync` 重新部署至全域 `~/.claude/skills/`。
