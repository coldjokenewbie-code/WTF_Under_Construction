# 專案註冊表（projects-registry）

> SSOT：本檔取代 `extra-scan-dirs.txt`，並吸收 machines.md 的「路徑」用途。
> 主鍵＝專案名稱；每專案 × 每機器一列，列出該機實體路徑。
> `sync_config.py` 依本機 hostname 過濾 `path` 欄 → 即為要寫副本的專案清單。
> machines.md 改只留機器身分（hostname/OS/別名/最後出現）。
>
> 維護規則：
> - 新增專案或換機 → 只改本表。
> - `path` 留空 = sync 跳過該機該專案（尚未部署）。
> - 機器 hostname 見 machines.md。
> - WTF_Under_Construction repo 本身已移出 Drive（兩機 Git_work），故其 path 指 Git_work；其餘專案仍在 Drive。

| project | machine (hostname) | path |
|---|---|---|
| WTF_Under_Construction | comaMacBookAir.local | /Users/coma/Git_work/WTF_Under_Construction |
| WTF_Under_Construction | DESKTOP-7SF21LR | E:\Git_work\WTF_Under_Construction |
| Aseembly_Plant | comaMacBookAir.local | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/Aseembly_Plant |
| Aseembly_Plant | DESKTOP-7SF21LR | E:\Claude_cowork\projects\Aseembly_Plant |
| HsinchuScienceEducationCenter | comaMacBookAir.local | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/HsinchuScienceEducationCenter |
| HsinchuScienceEducationCenter | DESKTOP-7SF21LR | E:\Claude_cowork\projects\HsinchuScienceEducationCenter |
| cowork_CDIC | comaMacBookAir.local | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/cowork_CDIC |
| cowork_CDIC | DESKTOP-7SF21LR | E:\Claude_cowork\projects\cowork_CDIC |
| 出勤專案 | comaMacBookAir.local | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/出勤專案 |
| 出勤專案 | DESKTOP-7SF21LR | E:\Claude_cowork\projects\出勤專案 |
| 南科再生水廠 | comaMacBookAir.local | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/南科再生水廠 |
| 南科再生水廠 | DESKTOP-7SF21LR | E:\Claude_cowork\projects\南科再生水廠 |
| 國圖南 | comaMacBookAir.local | /Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/國圖南 |
| 國圖南 | DESKTOP-7SF21LR | E:\Claude_cowork\projects\國圖南 |
| Assembly_Plant_Mobile_Guide | comaMacBookAir.local | /Users/coma/Git_work/Assembly_Plant_Mobile_Guide |
| Assembly_Plant_Mobile_Guide | DESKTOP-7SF21LR | E:\Git_work\Assembly_Plant_Mobile_Guide |
| Planner2Line | comaMacBookAir.local | /Users/coma/Git_work/Planner2Line |
| Planner2Line | DESKTOP-7SF21LR | E:\Git_work\Planner2Line |
| Remotion_fun | comaMacBookAir.local | /Users/coma/Git_work/Remotion_fun |
| Remotion_fun | DESKTOP-7SF21LR | E:\Git_work\Remotion_fun |
| claude_CDIC_O4 | comaMacBookAir.local | /Users/coma/Git_work/claude_CDIC_O4 |
| claude_CDIC_O4 | DESKTOP-7SF21LR | E:\Git_work\claude_CDIC_O4 |
