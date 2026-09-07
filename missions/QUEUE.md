# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**提醒棒 2026-09-07 19:00**：佇列現況——**0 active**／2 待核准／2 parked／2 done／5 提名。今晚循環棒（19:30/21:30/23:30/01:30台北）若無使用者動作，將延續**連續45天零增量**紀錄全數秒退。
**待核准/提名清單**：`20260706-guide-app`（優先2，backlog 19項剩6項未勾，待2項blocker裁決後可續跑）／`test-baton-pickup-0706`（優先9，backlog全勾，建議直接結案改done或刪列，免佔佇列）；5項提名（`ody-evidence-gate`／`southlibrary-fonts`／`cowork-c-tasks`／`sreclaim-verify-b`／`pptmap-skill`）多數待補掛來源repo，其餘待使用者核准升「待規劃」。
**blockers待決**：`machine-report`逾期**48天**（自2026-07-21起算，待使用者補充具體修正意見，否則無法判斷小修或整篇重寫）／`guide-app`——氛圍底圖/縮圖/hero照風格統一路線待重拍截圖裁決＋定錨稽核提案（字級收斂驗收方法論升級）待裁決，2026-07-21已提示回覆待補／`design-training`（案例包僅本機執行，非待裁決，非阻塞）。
**產能算術（義務）**：現無 active 案，剩餘backlog項數＝N/A；今晚排定循環棒4棒。若`guide-app`今晚獲核准改active：剩餘6項backlog，依「每棒一項」推算約需6棒（輪替制下與其他active案並行則更久）；若`test-baton-pickup-0706`今晚獲核准，backlog已全勾可直接改done，不耗棒。兩者皆未核准則今晚4棒預計全數秒退，完成日不適用。
**建議**：`test-baton-pickup-0706`可立即結案（改done或刪列）；`guide-app`兩項blocker任一裁決即可解鎖6項backlog續跑。

## 佇列

| slug | 狀態 | 優先序(1最高) | 一句話方向 |
|---|---|---|---|
| 20260706-machine-report | parked | 1 | 互動機具設計報告書（億元標案等級）；**2026-07-21 使用者驗收未過，暫時擱置**，待使用者補充具體修正意見（見 _blockers.md），補充後改回待核准/active |
| 20260706-guide-app | 待核准 | 2 | 【2026-07-08 改向】優化現有 app（Assembly_Plant_Mobile_Guide，分支 ui-uplift）：M2 界達成（增量一～八，audit #6/#7 全數完成）。**2026-08-11 使用者裁定主題方向A（暗色為主）**，細節記於專案本身 TaskLog；剩餘卡點：氛圍底圖/縮圖/hero照風格統一路線（待重拍截圖後裁決）＋anchor 升級提案，見 backlog/_blockers |
| 20260706-o4-soundtrack | done | — | 使用者 2026-08-11 確認已結案（結案細節未展開，未再回收），棒子不再排入 |
| 20260707-design-training | parked | 4 | 使用者設計能力訓練支援（常設,週循環）。**2026-07-21 使用者裁決**：案例包改僅本機(Mac)執行，雲端棒固定跳過；本週雲端無可作項（批評官值勤同樣本機限定,月審未到期），非待裁決卡點 |
| test-baton-pickup-0706 | 待核准 | 9 | 管線探針：三檔齊備＋成功推 night-relay，無實質產出。**2026-07-24 01:30 棒（連續2晚缺席後第3次機會）成功觸發**，backlog 全勾，建議使用者直接結案（改「done」或刪列即可，無需續跑） |
| 20260721-session-gate-fix | done | — | 已於 2026-07-22 由使用者直接指示當下 session 修復（跳過夜間棒）：postread exists 檢查＋bundle SHA 改讀 CLAUDE.md 權威來源。PreToolUse/Stop 接線經詢問使用者後暫不做。詳見 `_context/TaskLog_2026-07-21_session-gate診斷.md`（main 34f5602 直接修復，優先於 night-relay 排程狀態） |
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
