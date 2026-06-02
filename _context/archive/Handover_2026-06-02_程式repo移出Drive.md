# 交接文件 2026-06-02 — 程式 repo 移出 Drive 改純 git 管理

## 1. 現況摘要
工作區正式分兩區：
- **`E:\Claude_cowork`（Drive 同步）**：文書、素材、SSOT（wtf-config）。
- **`E:\Git_work`（非 Drive，純 git）**：程式 repo。

本次把 5 個程式 repo 從 Drive 移到 `E:\Git_work`，並修復一個 Drive 造成的檔案損壞。動機已被實證：claude_CDIC_O4 在 Drive 內掉了 90 個檔（含程式碼）。

## 2. 檔案位置
- 已移出（在 `E:\Git_work\`）：Assembly_Plant_Mobile_Guide、Remotion_fun、claude_CDIC_O4、notebooklm-skill、Plnner2Line。
- 仍在 Drive（素材重／SSOT，刻意不搬）：cowork_CDIC、HsinchuScienceEducationCenter、國圖南、WTF_Under_Construction。
- SSOT：`E:\Claude_cowork\projects\WTF_Under_Construction\wtf-config\`
- 全域 bootstrap：`C:\Users\2025.DESKTOP-7SF21LR\.claude\CLAUDE.md`（URL 已修為 wtf-config）

## 3. 緊急修復
無 P0。已修復項：claude_CDIC_O4 的 90 檔損壞已從 git HEAD 還原完畢。

## 4. 技術細節
- **兩區載入機制不同**：
  - Drive 區：靠專案層指標檔 `E:\Claude_cowork\CLAUDE.md` 讀**本機** wtf-config。
  - Git_work 區：無本機 wtf-config，靠全域 `~/.claude/CLAUDE.md` 的 **GitHub raw URL** 抓 wtf-config（URL 與磁碟位置無關，兩區皆可用）。
- **正確 raw URL**（已驗 200）：
  `https://raw.githubusercontent.com/coldjokenewbie-code/WTF_Under_Construction/main/wtf-config/GLOBAL.md`
  `.../wtf-config/CLAUDE_CODE.md`
- **搬移注意**：Drive 內資料夾若被 IDE/agent（Antigravity、node、codex）開著會鎖檔，rename 報 Access denied。需先關程式或由使用者手動搬。
- **commit 排除清單**：`AGENTS (1).md`（Drive 重複命名孤兒）、`out/`、`.pycache/`、build 產物。
- **git push 護欄**：auto-mode 分類器擋直推預設分支；使用者明確指示「push」即放行。agent 不能自改 settings.json 放寬（self-modification 護欄）。

## 5. 後續待辦
1. **lesson 寫入**：Drive 同步 .git 會損壞 repo → 寫進 `wtf-config/GLOBAL.md`「檔案存放」段（本次已提議、待確認）。
2. **修 lesson-add skill**：路徑 `claude-config/` → `wtf-config/`。
3. **notebooklm-skill remote**：無 claude-world 寫入權，決定 fork/換 remote/維持本機。
4. **跨機**：其他桌機 (a) `~/.claude/CLAUDE.md` URL 改 wtf-config；(b) `git clone` 取得 E:\Git_work 各 repo。
5. **接前次交接**：T2 skills 漂移整治、T3 Drive 排除剩餘項（見 `Handover_2026-06-02_工作區整合.md`）。
