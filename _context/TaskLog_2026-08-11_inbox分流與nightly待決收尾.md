# TaskLog 2026-08-11：inbox 分流（含撤回）＋ to-codex skill 分享包＋ nightly 待決收尾

## 完成項目

### 1. `/inbox` 語音待辦分流（cowork_CDIC）→ 使用者要求撤回
- 三筆 Obsidian 語音速記分流進 cowork_CDIC 各區 TaskLog（A/B/C/E/O 區＋新建跨區彙整檔）＋鏡像進 `ai-team-todo`（25 筆，owner=AI）。
- 使用者反饋「App 內容寫不清楚」，要求完整撤回：TaskLog 還原（Drive 為 SSOT，改完重跑 `mirror_sync.sh` 產生對稱 revert diff）、mirror repo commit `e60500b` 撤回並 push、`ai-team-todo` 25 筆全刪、3 份語音速記搬回 `Clippings/`。
- **教訓**：`ai-team-todo` 既有多筆專案名稱誤將「頂層/子專案」字面塞進單一 `--project` 值（`CDIC/現場安裝`、`出勤/儀錶板`、`組立/導覽` 等 22 筆），已修正並存入記憶；`--project`/`--sub` 必須分開傳。

### 2. `/to-codex` skill：把工作交辦給 Codex CLI（ChatGPT 帳號登入，非 API）
- 確認本機 Codex CLI 走 `auth_mode: chatgpt`（非 API key）。
- 設計並反覆修訂 `to-codex` skill（`SKILL.md`）：先查 codex 安裝／登入狀態，缺一即停並引導使用者；備妥後把交辦文字轉發 `codex exec ... -s read-only --skip-git-repo-check < /dev/null`。
- 依使用者指示定案：個人層級分享（非專案層級）；預設唯讀（非 workspace-write）；升級寫入權限前**由 Claude Code 讀交辦文字裡的資料夾路徑自己 cd**，不要求同事操作終端機。
- 產出 HTML 安裝說明（3 頁簽：懶人設定／依序設定／常見問題；頂部用法說明改紅字），打包成 `to-codex-分享包.zip`，位置定案在 `workingfiles/outputs/to-codex-分享包/`（原本誤放 session scratchpad，經使用者指正搬移；同時把舊有的頂層 `outputs/` 併入 `workingfiles/outputs/`，符合 GLOBAL.md 現行資料夾規範）。

### 3. nightly 待決三項收尾（使用者當面裁示）
- **agy headless Mac 平台修法**：核准套用；但 `nightly-notify.md` 指的目標檔（`wtf-config/GLOBAL.md`）是錯的，實際條目在 `tools/ai-team/cli-reference.html`——已在正確位置補上 Mac 平台解法（stdin 進不了模型，改用 `agy --print "<prompt>" --dangerously-skip-permissions` 命令列參數），`nightly-notify.md` 該項勾掉並註明指錯檔。
- **`20260706-o4-soundtrack` mission**：使用者確認已結案，`missions/QUEUE.md` 改 done、`_blockers.md` 全勾起來標註結案，不再排入夜棒。
- **`20260706-guide-app` 主題定調**：使用者裁定 A（暗色為主）。**依使用者糾正**：決策細節改記在專案本身（`Assembly_Plant_Mobile_Guide/_context/TaskLog_2026-08-11_UI優化與主題定調.md`＋`INDEX.md` 補指標），WTF 層級 `missions/20260706-guide-app/_blockers.md` 只留指標，不重複放內容——避免兩處各存一份會漂移。附但書：此裁定未必是在「CDN 修好後可信截圖」基礎上做的，執行棒動工前應先補拍確認。

## 意外發現（重要，需留意）
本 session 的暫存 git 變更（`outputs`→`workingfiles/outputs` 改名＋新增 to-codex 分享包）**被另一個並行 session 的 commit（`d9e6f39`，作者 Claude Opus 5，session `01Fpyeh4FrHNqxktpaGxmyT5`）意外一併帶走並已推送**——內容經核對正確無誤（`git show --stat d9e6f39` 逐檔比對相符），但 commit message 與本 session 工作無關（該 commit 名義上是「CDIC B 區 lessons 索引」）。
**根因**：WTF_Under_Construction 本機 checkout 沒有用 git worktree 隔離，多個 session 共用同一份工作目錄／git index；我方已 `git add` 但未 commit 的變更，被另一 session 的 commit 動作一併吃進去。
**這次無資料損失**（內容已核對正確且已推送），但屬於流程風險，值得之後考慮：本機多 session 平行工作 WTF repo 本身時，是否也該比照 cowork_CDIC 的「大量並行改動」現實，改用 `git worktree` 隔離（見 `wtf-config/playbooks/parallel-worktree.md`）。

## 下一步
- `Assembly_Plant_Mobile_Guide/_context/` 那項風格統一裁決（氛圍底圖／展品縮圖／hero 史料照）尚未問使用者。
- `ody-squad-dispatch`（`tools/ody/squad/coach.py` 加分工機制）計畫已寫好在 `~/.claude/plans/swift-sauteeing-owl.md`，本 session 未動工，待使用者指示續辦。
