# TaskLog 2026-07-15：git_mirror 跨機部署與 Git_work 整併

> 🪟 **[Claude@Win] 開場必讀**：你這台的任務＝Git_work 整併＋WTF 搬家善後，完整步驟在
> `_context/Handover_2026-07-15_Windows-Git_work整併.md`——先讀該檔照做（階段 0 最優先，hook 修好前每個 prompt 都會報同步失敗）。
> 本節由 [Claude@Mac] 2026-07-15 寫入；Windows 完成後刪本節並在下方追記。

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

## 未解決問題

- P1：Windows 端兩份 prompt（cowork_CDIC 系 7 專案 clone；Git_work 系 9 專案整併）都還沒實際執行，`projects-registry.md` 的 Windows 欄位目前是「待搬」佔位，非真實現況。
- P2：`VoiceInk` fork 之後，`_context/INDEX.md` 或類似指路文件沒有補（這個專案原本不在任何登記表內，屬於這次順手納管，尚未建立完整專案文件慣例）。
- P2：使用者曾手動把 `WTF_Under_Construction` 移到 git_mirror 再移回來（實驗性動作，session 內觀察到工作目錄短暫消失又復原），最終結論是 WTF 本體維持原地不動、不進 git_mirror（跟其他專案不同，屬既定例外）。

## 主要輸入檔案

- `wtf-config/GLOBAL.md`「Claude_cowork 專案的版控架構」段（本次擴充）
- `wtf-config/projects-registry.md`（本次大改）
- 送出的兩份 Windows prompt（未落檔在 repo 內，僅交付使用者，內容摘要見上）

## 下一步建議

1. 使用者在 Windows 依序跑完兩份 prompt，回報後把 `projects-registry.md` 的「待搬」欄位更新成實際路徑。
2. 有空幫 `VoiceInk` 補一份最小 `_context/INDEX.md`（fork 緣由、上游同步策略），納入正常專案文件慣例。
