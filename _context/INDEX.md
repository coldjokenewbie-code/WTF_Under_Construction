# WTF_Under_Construction — 現況總覽 (INDEX)
> 進場先讀。**本檔只指路，不複製 todo**（todo 真相源＝當前 TaskLog）。最後更新：2026-06-03

## 一句話目標
Workflows That Flow：以複利累積跨工具（Claude Code／Cowork／Codex／Antigravity）協作效率與效益。本專案＝全域設定與 Skills 的真相源（SSOT）。

## 現況（一句話）
階段二完成、**兩機收斂、Mac 驗收 PASS、無分叉**：整個 WTF repo 移出 Drive（兩機 Git_work），放棄 split。hook 只 `git pull`＋`sync`、不 auto-commit。skills 命名/規範已對齊（TaskLog_、session-start 增 rules＋身分宣告）；registry 已登記 Windows Git_work repos；新增跨機/跨工具「記錄署名」慣例。WTF skills 已跨工具部署（Windows 的 Codex／Gemini，`deploy_other_tools()`）；常駐 monitor 僅 ai-team＋明示跨機討論才開（餘靠 INDEX/TaskLog 非同步交棒）。

## 關鍵檔
- SSOT：`wtf-config/GLOBAL.md`、`wtf-config/AGENTS.md`、`wtf-config/sync_config.py`、`wtf-config/projects-registry.md`（專案×機器×路徑）
- 🖥️跨機即時協調（Drive，非 repo）：`E:\Claude_cowork\projects\Git_work_agents\WTFrepo\signals_WIN.md`／`signals_MAC.md`（per-machine 單寫檔，見下「讀取指引」）
- 同步架構決策：`workingfiles/SSOT同步架構討論_2026-06-03.md`（結論段）
- 最新工作紀錄：`_context/TaskLog_2026-06-03_階段二-移出Drive.md`
- 交接/階段一已 archive：`_context/archive/`
- lessons：`_context/lessons-learned.md`、雲端層 `wtf-config/LESSONS.md`

## 讀取指引（指路，只讀必要文件）
> 🖥️＝含對方機器內容的跨機檔；看 byline `[Claude@Win/Mac]` 辨歸屬，**非己作不必重讀**。
- **接手階段二/同步架構**：讀 `TaskLog_2026-06-03_階段二-移出Drive.md` ＋ 🖥️Drive `signals_WIN.md`/`signals_MAC.md`（跨機現狀），其餘跳過。
- **只查教訓**：`_context/lessons-learned.md`（詳述）／`wtf-config/LESSONS.md`（雲端索引）。
- **改同步腳本/registry**：`wtf-config/sync_config.py` ＋ `projects-registry.md`，不必讀 workingfiles 討論全文。
- 跨機協作前先看 session-start 的「身分宣告」確認自己是哪台/哪工具。

## 架構要點（已定案）
- 全實體副本，放棄 symlink（Drive 跨平台失效）。
- 自動同步＝UserPromptSubmit hook + 5 分冷卻（兩端統一）；`session-start` skill 只核對＋讀知識，不重工。
- `sync_config.py` 由 `projects-registry.md` 取本機 hostname 的專案清單（絕對路徑）；`deploy_claude_dir()` 逐 skill 容錯覆蓋（不整批 rmtree）。
- **階段二（已執行）**：整個 WTF repo 移出 Drive（兩機 Git_work），非 split。hook 只 `git pull`＋`sync`、不清 lock、不 auto-commit（commit 手動）。其餘 6 個 Drive 專案不動，續吃 sync 副本。

## 待用戶拍板（決策閘，非工作線 todo）
1. Antigravity 原生 Gemini 是否只認 `GEMINI.md`（需實測，決定要不要產第二種副本）。
2. （可選）清理 project `.claude/settings.json` 殘留死路徑（claude-config 舊名、Mac Drive 絕對路徑、Git_foler_anti）——本次 auto-mode 擋下 agent 改 settings，待用戶手動清。

## 備註
- Windows 跑 `sync_config.py` 若遇 cp950 中文錯誤，先 `$env:PYTHONIOENCODING="utf-8"`（腳本已 reconfigure，多數情境免）。
