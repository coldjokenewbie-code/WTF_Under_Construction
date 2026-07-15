# 專案註冊表（projects-registry）

> SSOT：本檔取代 `extra-scan-dirs.txt`，並吸收 machines.md 的「路徑」用途。
> **格式＝專案為主**：每專案一列，欄含 `github` 與各機器（欄頭＝hostname）的實體路徑。
> `sync_config.py` 讀表頭，取「欄頭 == 本機 hostname」那欄的路徑 → 即本機要寫副本/掃描的專案清單。
> github 欄供 `/inbox` 等流程用（分流落地後 commit/push 對應 repo）。
> 多數專案皆 github 版控（大檔不入 git，git 只做版控）；少數鏡像內未見 .git 者標「待確認」。
>
> 維護規則：
> - 新增專案或換機 → 只改本表。新機器＝加一欄（欄頭填該機 hostname，見 machines.md）。
> - 機器欄留空 = sync 跳過該機該專案（尚未部署）。
> - 路徑佔位用全形括號「（…）」開頭 → 視為未部署、sync 略過；github 欄同樣以「（…）」標未確認。
> - WTF_Under_Construction：Mac／Windows 皆已搬入 `git_mirror/`（2026-07-15）；Claude_cowork 專案的 Mac 路徑為 Google Drive「其他電腦」對 Windows 的鏡像。
> - **2026-07-15 整併**：純 code 專案（無 Drive 對應）已從 Git_work 遷到 `git_mirror/`（Mac 已執行，舊 Git_work 副本移入 `Git_work/git_work_bk/` 備份；Windows 待執行同步驟）。往後新純 code 專案一律直接建在 `git_mirror/`，不再放 Git_work。

| project | github | comaMacBookAir.local | DESKTOP-7SF21LR |
|---|---|---|---|
| WTF_Under_Construction | https://github.com/coldjokenewbie-code/WTF_Under_Construction.git | /Users/coma/git_mirror/WTF_Under_Construction | E:\git_mirror\WTF_Under_Construction |
| ai-team-todo | https://github.com/coldjokenewbie-code/ai-team-todo.git | /Users/coma/git_mirror/ai-team-todo | E:\git_mirror\ai-team-todo |
| Assembly_Plant_Mobile_Guide | https://github.com/coldjokenewbie-code/Assembly_Plant_Mobile_Guide.git | /Users/coma/git_mirror/Assembly_Plant_Mobile_Guide | E:\git_mirror\Assembly_Plant_Mobile_Guide |
| Planner2Line | https://github.com/coldjokenewbie-code/Planner2Line.git | /Users/coma/git_mirror/Planner2Line | E:\git_mirror\Planner2Line |
| Remotion_fun | https://github.com/coldjokenewbie-code/Remotion_fun.git（branch master） | /Users/coma/git_mirror/Remotion_fun | E:\git_mirror\Remotion_fun |
| claude_CDIC_O4 | https://github.com/coldjokenewbie-code/claude_CDIC_O4.git（branch v615） | /Users/coma/git_mirror/claude_CDIC_O4 | E:\git_mirror\claude_CDIC_O4 |
| capture_app | https://github.com/coldjokenewbie-code/capture_app.git | /Users/coma/git_mirror/capture_app | E:\git_mirror\capture_app（待搬） |
| say-something | https://github.com/coldjokenewbie-code/say-something.git | /Users/coma/git_mirror/say-something | E:\git_mirror\say-something（待搬） |
| say-something-android | https://github.com/coldjokenewbie-code/say-something-android.git | /Users/coma/git_mirror/say-something-android | E:\git_mirror\say-something-android（待搬） |
| gen-tools | （無 remote，本機 only，個人腳本） | /Users/coma/git_mirror/gen-tools | （待確認） |
| VoiceInk | https://github.com/coldjokenewbie-code/UmaVoiceInk.git（**fork 自 Beingpax/VoiceInk，2026-07-15 已改指向自己帳號**） | /Users/coma/git_mirror/VoiceInk | E:\git_mirror\VoiceInk（待搬） |
| attendance-dashboard | https://github.com/coldjokenewbie-code/attendance-dashboard.git | /Users/coma/git_mirror/attendance-dashboard | E:\git_mirror\attendance-dashboard |
| Aseembly_Plant_Interactive_machine | git@github.com:coldjokenewbie-code/Aseembly_Plant_Interactive_machine.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/Aseembly_Plant_Interactive_machine | E:\Claude_cowork\projects\Aseembly_Plant_Interactive_machine |
| HsinchuScienceEducationCenter | git@github.com:coldjokenewbie-code/HsinchuScienceEducationCenter.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/HsinchuScienceEducationCenter | E:\Claude_cowork\projects\HsinchuScienceEducationCenter |
| cowork_CDIC | https://github.com/coldjokenewbie-code/cowork_CDIC.git（branch code-mirror） | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/cowork_CDIC | E:\Claude_cowork\projects\cowork_CDIC |
| 出勤專案 | https://github.com/coldjokenewbie-code/attendance-dashboard.git（**git_mirror 資料夾名已統一改用 `attendance-dashboard`，不再用「出勤專案」**） | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/出勤專案（mirror 見上方 attendance-dashboard 列） | E:\Claude_cowork\projects\出勤專案 |
| 南科再生水廠 | https://github.com/coldjokenewbie-code/S-reclaimed-water-plant.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/南科再生水廠 | E:\Claude_cowork\projects\南科再生水廠 |
| 國圖南 | git@github.com:coldjokenewbie-code/SouthLibrary.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/國圖南 | E:\Claude_cowork\projects\國圖南 |
| ppt_map_mark | git@github.com:coldjokenewbie-code/ppt_map_mark.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/ppt_map_mark | E:\Claude_cowork\projects\ppt_map_mark |
