# WTF_Under_Construction — 現況總覽 (INDEX)
> 進場先讀。**本檔只指路，不複製 todo**（todo 真相源＝當前 TaskLog）。最後更新：2026-06-03

## 一句話目標
Workflows That Flow：以複利累積跨工具（Claude Code／Cowork／Codex／Antigravity）協作效率與效益。本專案＝全域設定與 Skills 的真相源（SSOT）。

## 現況（一句話）
SSOT 跨機同步架構已定案；階段一重構執行中——Mac 端 `sync_config.py`／skills／git 已改完待 commit，Windows 端 settings 清理與 hook 腳本已備（hook 啟用待用戶授權）。

## 關鍵檔
- SSOT：`wtf-config/GLOBAL.md`、`wtf-config/AGENTS.md`、`wtf-config/sync_config.py`、`wtf-config/projects-registry.md`（專案×機器×路徑，取代 extra-scan-dirs.txt）
- 同步架構決策：`workingfiles/SSOT同步架構討論_2026-06-03.md`（結論段）
- 階段一執行／驗收紀錄：`workingfiles/階段一執行_2026-06-03.md`（含信號區）
- 最新交接：`_context/Handover_2026-06-03_全域設定自動同步架構重整.md`
- 最新工作紀錄：`_context/TaskLog_2026-06-03_全域設定自動同步架構重整.md`
- lessons：`_context/lessons-learned.md`、雲端層 `wtf-config/LESSONS.md`
- archive：`_context/archive/`

## 架構要點（已定案）
- 全實體副本，放棄 symlink（Drive 跨平台失效）。
- 自動同步＝UserPromptSubmit hook + 5 分冷卻（兩端統一）；`session-start` skill 只核對＋讀知識，不重工。
- `sync_config.py` 由 `projects-registry.md` 取本機 hostname 的專案清單；`deploy_claude_dir()` 逐 skill 容錯覆蓋（不整批 rmtree）。
- 階段二（待擇時）：`wtf-config` 抽成 Drive 外獨立 git repo，根除 .git lock。

## 待用戶拍板（決策閘，非工作線 todo）
1. 授權啟用 Windows `UserPromptSubmit` hook（settings.json）。
2. 授權 commit 階段一變更（main branch）。
3. 階段二（wtf-config 抽離 Drive）執行時機。
4. Antigravity 原生 Gemini 是否只認 `GEMINI.md`（需實測，決定要不要產第二種副本）。

## 備註
- Windows 跑 `sync_config.py` 若遇 cp950 中文錯誤，先 `$env:PYTHONIOENCODING="utf-8"`（腳本已 reconfigure，多數情境免）。
