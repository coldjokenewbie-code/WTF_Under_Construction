# TaskLog 2026-07-15：git_mirror 跨機部署與 Git_work 整併

> 承接 `TaskLog_2026-07-09_hook注入強制化與遵循度診斷.md` 提到的 git_mirror 機制。本次把機制從「cowork_CDIC 一個試點」擴展成「全部 Claude_cowork 專案 + 全部純 code 專案」的統一佈局，並清空 `Git_work/` 只留 `WTF_Under_Construction`。

## 完成項目

1. **cowork_CDIC 鏡像補推**：168 檔異動 commit+push（`3b58099`），驗證整套機制可用。
2. **6 個 Drive 專案 `_context/INDEX.md` 加註版控架構說明**（cowork_CDIC／Aseembly_Plant_Interactive_machine／HsinchuScienceEducationCenter／出勤專案／南科再生水廠／國圖南），避免以後在這些資料夾誤用 git skill；`ppt_map_mark` 無 INDEX.md，跳過未新建。
3. **解除卡住 5 天的 wtf-sync**：另一 session 草擬的 GLOBAL.md「Claude_cowork 版控架構」段一直沒 commit，跟遠端新 commit 撞在一起卡死 `git pull`；已 commit＋merge＋push，並設 `pull.rebase false` 避免同類錯誤再發生。GLOBAL.md 補上 Windows 路徑慣例（`E:\git_mirror\`）與「無 mirror 但有 remote 時該 clone 不該 Drive git init」判準。
4. **Windows git_mirror 建置 prompt**（第一階段）：7 個 Claude_cowork 專案的 clone 清單＋SSH fallback HTTPS 處理，已產出送出，待使用者在 Windows 執行。
5. **Git_work → git_mirror + git_work_bk 大整併**（Mac 端，經使用者逐點核准）：
   - 7 個有未 commit 異動的專案（ai-team-todo、Assembly_Plant_Mobile_Guide、claude_CDIC_O4、Planner2Line、Remotion_fun、say-something-android、VoiceInk）先 commit+push 清乾淨。
   - 9 個純 code 專案（上述扣 VoiceInk 加 capture_app／say-something／attendance-dashboard）：`git_mirror` fresh clone、`Git_work` 舊副本搬進 `Git_work/git_work_bk/`。
   - `gen-tools`：內容核對一致，直接歸檔（無 remote，git_mirror 本來就是完整版）。
   - `attendance-dashboard` vs `出勤專案` 重複 mirror：兩份都已各自 push 到 GitHub 不同分支，內容沒丟；統一留 `git_mirror/attendance-dashboard`（較完整），砍掉 `git_mirror/出勤專案`，回頭改 Drive 端 `出勤專案/_context/INDEX.md` 指路。
   - 3 個非常規歷史備份項目（`asembly_ppt.git`、`asembly_ppt.git.bak-20260630-2043`、`_asembly_premerge_backup_20260630`）整包歸檔，內容未動。
   - `VoiceInk`：remote 是他人 upstream（`Beingpax/VoiceInk`，403 無 push 權限）→ 使用者 fork 為 `coldjokenewbie-code/UmaVoiceInk` → 本機 remote 改指向、合併 10 個上游 commit、推送成功、git_mirror 重建、Git_work 歸檔。
   - `wtf-config/projects-registry.md` 全程同步更新（Mac 路徑改 git_mirror、Windows 路徑標「待搬」、VoiceInk 補 fork 說明）。
6. **Windows Git_work 整併 prompt**（第二階段）：9 個純 code 專案「確認乾淨→commit+push→重建 git_mirror→歸檔」流程，已產出送出，待使用者在 Windows 執行。
7. **WTF 本體路徑更新**（追記，使用者已手動把 WTF 從 `Git_work/` 搬入 `git_mirror/`）：registry／machines.md／`~/.claude/wtf-sync.sh`／兩份 settings 允許清單全數改指新路徑（commit `d584393`）；wtf-sync hook 的 pull 失敗根因即舊路徑，已實跑驗證恢復。
8. **出勤專案 Drive↔mirror 合併收尾**（追記）：`code-mirror-drive` 快照與 live Drive 逐檔比對，僅 `ai-team-agent-cli-reference.html`（角色分段改版）與 `workingfiles/test_ai_team.md` 為 Drive 獨有，已併入 attendance-dashboard main（`43a63b2`）；INDEX 兩邊統一（含版控警語＋Antigravity CLI 規格標完成，`9b85613`）；main 較新的 lessons／handover 反向複製回 Drive。sweep 後兩邊白名單檔案全一致（AGENTS.md 屬 sync 自動維護例外）。`code-mirror-drive`／`code-mirror-gitwork` 兩分支內容已全數吸收，使用者已刪除遠端分支。
9. **[Claude@Win] Windows 端 Handover 執行完成**（2026-07-15）：
   - **階段0**：`wtf-root.txt` 核對正確；`~/.claude/wtf-sync.ps1` 的 `$WTF` 改指 `E:\git_mirror\WTF_Under_Construction`；`projects-registry.md`／`machines.md` WTF 列改新路徑並 commit+push（`ca4bbcf`）。另外掃出 4 個專案（`attendance-dashboard`／`AgentIDE`／`attendance-0955`／`claude_CDIC_O4`）的 `.claude/settings.local.json` 也含舊 `E:\Git_work\WTF_Under_Construction` 路徑，一併修正（Handover 原文未預期此範圍，屬追加發現）。
   - **階段1**：`ai-team-todo`／`Assembly_Plant_Mobile_Guide`／`Planner2Line`／`Remotion_fun` 四個純 code 專案，各自「確認乾淨→commit/merge→push→fresh clone→歸檔 git_work_bk」完成；`attendance-dashboard`＋兩個 worktree（`attendance-0945`/`attendance-0955`）比照 Handover 特別指示，push 兩個 worktree 分支（遠端原本沒有，本次新建 `flow-0945`/`flow-0955`）後三個資料夾整包歸檔，不在 git_mirror 重建 worktree。
     - **意外發現**：`Assembly_Plant_Mobile_Guide`／`Planner2Line`／`claude_CDIC_O4` 三個專案本機工作目錄都嚴重落後遠端（另有其他 session／機器持續在推 commit），其中 `Assembly_Plant_Mobile_Guide` 本地未提交異動與遠端已推送的 `750c37a` 是**同一件事**（英文館名 Assembly Plant→Erecting Workshop）重複做，merge 時 `data/exhibits.ts` 撞出真實文字內容衝突，已與使用者確認採用哪版措辭後手動解衝突推送。
   - **claude_CDIC_O4 未完成**（見「未解決問題」P1）。
   - **階段2**：7 個 Claude_cowork 專案的 git_mirror clone **實際上已存在**（非本次新建，疑似之前已有其他 session 做過），逐一核對 remote／branch／clean 狀態皆正常；唯一問題是 `git_mirror/出勤專案` 與 `git_mirror/attendance-dashboard` 重複——核對後前者內容已完全併入後者（無獨有內容），經使用者確認後刪除。
   - registry「待搬」欄位已改回實路徑（各步驟隨手更新，非集中一次性改）。
10. **[Claude@Win] claude_CDIC_O4 補做完成**（2026-07-15，同日稍晚）：
    - 根因非網路環境問題，是這個 repo 本身 `.git` 高達 4.2GB（多支 70MB+ 影片、大圖、字型直接 commit 進歷史，`.gitignore` 只排除 `out/` 沒排除 `public/videos`／`images`／`fonts` 這些源素材），單次完整傳輸容易在這個網路環境中斷（`invalid index-pack output`）。
    - 改用 `git fetch --depth=1`／`--unshallow`（拉長逾時到 280s）逐步補齊本地歷史成功；merge 遠端 9 個新 commit（含夜間 routine 補的 lessons、雲端 session 的 V2 配樂/影片重製），`AGENTS.md`／`.claude/settings.local.json`／`_context/INDEX.md` 三處衝突手動解決（AGENTS.md／INDEX.md 各取較新一版；settings.local.json 兩機權限清單合併，但排除一條過寬的萬用字元規則 `Bash(python3 -c ' *)`，及使用者確認後一併拿掉的 `pip install *`／`npm install:*`／`git stash *`／`Read(//c/Users/user/**)` 四條中高風險規則）。
    - 全新 `git clone` 對這個大 repo 持續失敗（含 `--single-branch` 也一樣，新 clone 需一次傳輸全部歷史）；改用本機路徑 clone（`git clone <本地路徑> <git_mirror路徑>`，不經網路）產生 git_mirror 副本，再改 remote URL 指回 GitHub，達到與其他專案一致的乾淨副本效果。舊資料夾歸檔 `git_work_bk`，registry 改回實路徑。

## 未解決問題

- P2：`VoiceInk` fork 之後，`_context/INDEX.md` 或類似指路文件沒有補（這個專案原本不在任何登記表內，屬於這次順手納管，尚未建立完整專案文件慣例）。
- P2：使用者曾手動把 `WTF_Under_Construction` 移到 git_mirror 再移回來（實驗性動作，session 內觀察到工作目錄短暫消失又復原），最終結論是 WTF 本體維持原地不動、不進 git_mirror（跟其他專案不同，屬既定例外）。
- P2：`E:\Git_work\AgentIDE`（無 `.git`，`~/.claude/settings.json` 的 hook 寫死指向此路徑）與 `E:\Git_work\lathe`（獨立 git repo，有未提交異動含大型二進位檔）皆不在本次 Handover 範圍內，維持原地未動；`lathe` 在本次過程中曾被移入 `git_work_bk/`，非本 session 動作，來源不明，籲使用者自行核對其未提交異動是否需要處理。

## 主要輸入檔案

- `wtf-config/GLOBAL.md`「Claude_cowork 專案的版控架構」段（本次擴充）
- `wtf-config/projects-registry.md`（本次大改）
- 送出的兩份 Windows prompt（未落檔在 repo 內，僅交付使用者，內容摘要見上）

## 下一步建議

1. 有空幫 `VoiceInk` 補一份最小 `_context/INDEX.md`（fork 緣由、上游同步策略），納入正常專案文件慣例。
2. 使用者核對 `E:\Git_work\git_work_bk\lathe` 的未提交異動（大型二進位檔）是否需要處理。
3. `claude_CDIC_O4` 大檔（影片/圖片/字型）直接進 git 導致 `.git` 4.2GB，若之後還要跨機/跨網路環境同步，建議評估改用 Git LFS 或搬出 git 版控（非本次任務範圍，僅記錄觀察）。
