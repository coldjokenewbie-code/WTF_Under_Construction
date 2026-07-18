# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**晨報棒 2026-07-18 08:30**：night-relay 領先 main 95 commits但昨晚零新增（QUEUE 連續第7日0 active）——各 mission 無增量，狀態與昨日17:06快報完全無變動。**異常**：昨晚19:30/21:30兩棒完全未見於 heartbeat.log（含心跳都沒有，非正常秒退記錄），僅23:33/01:34兩棒有秒退心跳；與過去6晚每晚固定4筆心跳的模式不同，疑似trigger未觸發，僅供留意不代處置。
**待核准(3，同前)**：machine-report(P1,全篇+opus對抗審查PASS,待驗貨改done)／guide-app(P2,M2界達成增量一~八全勾,剩anchor升級提案+2項高品味主題裁決)／test-baton-pickup-0706(P9,探針驗證通過,建議直接結案)
**parked(2，待裁決解封，同前)**：o4-soundtrack(P3,卡【方向二拍板】或【硬底線4修訂提案】,_blockers 5條含兩分支待合併d8b50d8/80a8c9a)／design-training(P4,卡WebFetch全面403,_blockers 4選項待裁決)
**新 blockers**：無（皆既有卡點延續）
**提名(5，未掛載/待啟動，同前)**：ody-evidence-gate／southlibrary-fonts／cowork-c-tasks／sreclaim-verify-b／pptmap-skill
**產能算術（義務）**：0 active，backlog 0 項可作——已連續7日全秒退，無法推算完成日；恢復產出需使用者核准至少一項「待核准」或裁決任一 parked 卡點。
**合併建議（收貨＝以下指令）**：
`git fetch origin && git checkout main && git merge origin/night-relay --no-edit && git push origin main`

## 佇列

| slug | 狀態 | 優先序(1最高) | 一句話方向 |
|---|---|---|---|
| 20260706-machine-report | 待核准 | 1 | 互動機具設計報告書（億元標案等級）；內容全章＋fresh-context 對抗審查(opus)PASS 已完成,M1+M2+M3 併案送審,待核准後改 done |
| 20260706-guide-app | 待核准 | 2 | 【2026-07-08 改向】優化現有 app（Assembly_Plant_Mobile_Guide，分支 ui-uplift）：M2 界達成（增量一～八，audit #6/#7 全數完成），剩餘低風險項卡 anchor 升級提案待裁決，見 backlog/_blockers |
| 20260706-o4-soundtrack | parked | 3 | O4 配樂重做：先研究→使用者討論→才製作（討論閘未開前音樂增量一律 blocker）；語音剪接/畫面品質方向已獲使用者認可；**23:34 棒觸發停止閘（連續2棒零進展）**，卡點見 _blockers.md，裁決後改回 active |
| 20260707-design-training | parked | 4 | 使用者設計能力訓練支援（常設,週循環）；**parked**:WebFetch 全面403(組織政策非暫時),案例包卡點連續2棒零進展,見 _blockers.md 4選項待裁決 |
| test-baton-pickup-0706 | 待核准 | 9 | 管線探針：23:34 棒驗證通過（三檔齊備＋成功推 night-relay），無實質產出,建議使用者直接結案 |
| ody-evidence-gate | 提名 | — | tools/ody 加「完成需證據」機檢＋pytest |
| southlibrary-fonts | 提名 | — | 字體去 CDN（需掛 SouthLibrary） |
| cowork-c-tasks | 提名 | — | C 區 5 任務資料化（需掛 cowork_CDIC） |
| sreclaim-verify-b | 提名 | — | 100 句查證批次 B（需掛 S-reclaimed-water-plant） |
| pptmap-skill | 提名 | — | 拉線標註封裝 skill（需掛 ppt_map_mark） |

> 「提名」＝候選，棒子不碰；改「待規劃」即啟動。active 三項為 2026-07-06 晚間模具實測（使用者已核准，跳過規劃棒直接執行）。
> **今晚輪替規則**：milestone 即停（→待核准），下一棒接下一個優先序——三案輪流推進，不獨占整夜。
> **來源 repo 未掛載**：寫 blocker 結束本棒，禁 parked；掛載狀態見 mission-loop.md 第 6 節。

## 使用說明（給使用者）
- **派新工作**：加一行，狀態填「待規劃」。當晚 19:00 起循環棒會先跑規劃棒，產出 MISSION 後停下等你核准。
- **核准**：把該行狀態改成「active」（手機上跟任何 Claude session 說也行）。
- **暫停**：改「parked」；**調順序**：改優先序數字。
- 卡點決策看各 mission 資料夾的 `_blockers.md`；17:00 快報會彙整。
