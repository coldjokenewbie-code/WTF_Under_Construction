# Handover 2026-07-15：Windows Git_work 整併＋WTF 搬家善後
> 執行者：Claude@DESKTOP-7SF21LR（Windows）。撰寫：[Claude@Mac]
> 前提：使用者已手動把 `E:\Git_work\WTF_Under_Construction` 移到 `E:\git_mirror\WTF_Under_Construction`。
> Mac 端對應工作已完成，參照 commit：`d584393`（路徑更新）、`311172c`（TaskLog 追記）；本檔＝Windows 對齊版，取代先前口頭交付的兩份 prompt（未落檔，以本檔為準）。

## 目標與動機
與 Mac 端佈局對齊：`E:\Git_work\` 清空成只剩 `git_work_bk\`（備份），所有純 code 專案改為 `E:\git_mirror\` fresh clone；WTF 搬家後修正全部本機錨點。Mac 端最終佈局可參照（git_mirror 18 專案，含中文名資料夾照專案名）。

## 通用規則
- Windows python 指令＝`python`（非 python3）。
- git 讀輸出一律 `-c core.quotepath=false`（中文檔名防八進位跳脫）。
- 各 repo 的 `AGENTS.md` 若只差 header 時間戳＝sync 重寫造成，`git checkout -- AGENTS.md` 還原即可，不算真變更（見 lessons 2026-07-15）。
- `git@github.com:` URL 若 SSH 失敗，改用 `https://github.com/` 同 repo URL。
- 每階段完成即在本檔勾選並回報，byline `[Claude@Win]`。

## 階段 0：WTF 搬家善後（最先做，hook 修好前每個 prompt 都會報同步失敗）
- [ ] 1. 核對 `~/.claude/wtf-root.txt` 內容＝`E:\git_mirror\WTF_Under_Construction`。不對→跑 `python E:\git_mirror\WTF_Under_Construction\wtf-config\sync_config.py sync`（sync 會依腳本自身位置重寫錨點）。
- [ ] 2. 改 `~/.claude/wtf-sync.ps1` 內 `$WTF` 變數→新路徑（UserPromptSubmit hook，改完下個 prompt 生效；這正是 Mac 端 pull 失敗的根因，同型修法）。
- [ ] 3. `~/.claude/settings.json` 與各專案 `.claude/settings.local.json` 允許清單中 `E:\Git_work\WTF_Under_Construction` 字串全數替換為新路徑（無則跳過）。
- [ ] 4. 更新 SSOT 並推送：`wtf-config/projects-registry.md` WTF 列 DESKTOP-7SF21LR 欄、`wtf-config/machines.md` DESKTOP-7SF21LR 列 workspace_root → `E:\git_mirror\WTF_Under_Construction`；跑 `register`＋`check` 驗證無 WARN；commit＋push main。

## 階段 1：Git_work 純 code 專案整併（主體）
先 `ls E:\Git_work\` 盤點實況（以現場為準，勿只信登記表）。對其中每個專案資料夾（`git_work_bk\` 除外），逐一執行「確認乾淨→push→重建→歸檔」：

- [ ] 1. `git -c core.quotepath=false status --porcelain`：真變更→commit；只有 AGENTS.md 時間戳→還原。
- [ ] 2. `git branch -vv` 檢查**所有本地分支**是否已 push；有 unpushed→push。
   - ⚠ **attendance 系特別注意**：`E:\Git_work\attendance-0945`／`attendance-0955` 是 worktree（依附 `attendance-dashboard` 主 repo）。GitHub remote 目前**只有 main**（flow-0945／flow-0955 遠端不存在，flow-0955 已併入 main）。若 worktree 本地分支有未推 commit，先 push 分支；確認無遺失後，worktree 資料夾隨主 repo 一起進 git_work_bk，**不在 git_mirror 重建 worktree**。
- [ ] 3. 乾淨後 fresh clone：`git clone <URL> E:\git_mirror\<專案名>`。URL 與預設分支查 `wtf-config/projects-registry.md`（Remotion_fun＝master、claude_CDIC_O4＝v615；VoiceInk 用 fork `UmaVoiceInk.git`，資料夾名仍 VoiceInk）。
- [ ] 4. 舊資料夾整個移入 `E:\Git_work\git_work_bk\`（無此夾先建）。
- [ ] 5. registry 該列 Windows 欄去掉「（待搬）」改實路徑。
- **gen-tools 例外**：無 remote 不能 clone。Windows 若有此資料夾→整個「移動」到 `E:\git_mirror\gen-tools`（保留 .git）並回報；沒有→registry 維持（待確認）。
- **驗收**：`E:\Git_work\` 只剩 `git_work_bk\`；每個 `E:\git_mirror\<專案>` `git status` 乾淨且 `git log -1` 與 GitHub 一致。

## 階段 2：Claude_cowork 專案 mirror clone
依 GLOBAL.md「Claude_cowork 專案的版控架構」，把 Drive 系專案的 mirror clone 到 `E:\git_mirror\`（資料夾名照下列，與 Mac 一致；已存在者跳過）：

| clone 到 | repo |
|---|---|
| `E:\git_mirror\Aseembly_Plant_Interactive_machine` | `coldjokenewbie-code/Aseembly_Plant_Interactive_machine` |
| `E:\git_mirror\HsinchuScienceEducationCenter` | `coldjokenewbie-code/HsinchuScienceEducationCenter` |
| `E:\git_mirror\cowork_CDIC` | `coldjokenewbie-code/cowork_CDIC`（branch code-mirror） |
| `E:\git_mirror\attendance-dashboard` | 階段 1 已涵蓋（=出勤專案 mirror，資料夾名統一用 repo 名） |
| `E:\git_mirror\南科再生水廠` | `coldjokenewbie-code/S-reclaimed-water-plant` |
| `E:\git_mirror\國圖南` | `coldjokenewbie-code/SouthLibrary` |
| `E:\git_mirror\ppt_map_mark` | `coldjokenewbie-code/ppt_map_mark` |

Drive 端（`E:\Claude_cowork\projects\…`）一律不動、不 git init。

## 收尾
- [ ] registry／machines 變更 commit＋push main。
- [ ] 在 `_context/TaskLog_2026-07-15_git_mirror跨機部署與Git_work整併.md` 追記 Windows 完成節（byline `[Claude@Win]`），並把「未解決問題 P1」標結。
- [ ] 全部完成後，本檔照慣例移 `_context/archive/`。
