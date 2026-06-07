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
> - WTF_Under_Construction repo 在兩機 Git_work；Claude_cowork 專案的 Mac 路徑為 Google Drive「其他電腦」對 Windows 的鏡像。

| project | github | comaMacBookAir.local | DESKTOP-7SF21LR |
|---|---|---|---|
| WTF_Under_Construction | https://github.com/coldjokenewbie-code/WTF_Under_Construction.git | /Users/coma/Git_work/WTF_Under_Construction | E:\Git_work\WTF_Under_Construction |
| Assembly_Plant_Mobile_Guide | https://github.com/coldjokenewbie-code/Assembly_Plant_Mobile_Guide.git | /Users/coma/Git_work/Assembly_Plant_Mobile_Guide | E:\Git_work\Assembly_Plant_Mobile_Guide |
| Planner2Line | https://github.com/coldjokenewbie-code/Planner2Line.git | /Users/coma/Git_work/Planner2Line | E:\Git_work\Planner2Line |
| Remotion_fun | https://github.com/coldjokenewbie-code/Remotion_fun.git | /Users/coma/Git_work/Remotion_fun | E:\Git_work\Remotion_fun |
| claude_CDIC_O4 | https://github.com/coldjokenewbie-code/claude_CDIC_O4.git | /Users/coma/Git_work/claude_CDIC_O4 | E:\Git_work\claude_CDIC_O4 |
| Aseembly_Plant_Interactive_machine | git@github.com:coldjokenewbie-code/Aseembly_Plant_Interactive_machine.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/Aseembly_Plant_Interactive_machine | E:\Claude_cowork\projects\Aseembly_Plant_Interactive_machine |
| HsinchuScienceEducationCenter | git@github.com:coldjokenewbie-code/HsinchuScienceEducationCenter.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/HsinchuScienceEducationCenter | E:\Claude_cowork\projects\HsinchuScienceEducationCenter |
| cowork_CDIC | https://github.com/coldjokenewbie-code/cowork_CDIC.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/cowork_CDIC | E:\Claude_cowork\projects\cowork_CDIC |
| 出勤專案 | git@github.com:coldjokenewbie-code/attendance-dashboard.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/出勤專案 | E:\Claude_cowork\projects\出勤專案 |
| 南科再生水廠 | https://github.com/coldjokenewbie-code/S-reclaimed-water-plant.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/南科再生水廠 | E:\Claude_cowork\projects\南科再生水廠 |
| 國圖南 | git@github.com:coldjokenewbie-code/SouthLibrary.git | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/國圖南 | E:\Claude_cowork\projects\國圖南 |
