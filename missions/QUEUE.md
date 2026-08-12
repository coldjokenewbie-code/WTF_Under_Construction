# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**提醒棒 2026-08-12 19:00**：併 origin/main 進 night-relay 時 QUEUE.md／2 個 _blockers.md 三檔衝突——main 直接記了 2 筆新使用者裁決（o4-soundtrack 08-11 確認結案、guide-app 主題定調裁定A暗色），但 main 的 QUEUE 狀態欄本身是 07-08 舊快照（07-29 才首次寫入 main，之後只動過一行），已人工合併：保留 night-relay 追蹤的正確狀態（parked/待核准），只採用 main 的兩筆新裁決；guide-app anchor 升級提案等既有卡點未被 main 觸及，已補回不遺失。QUEUE 現況：parked×2（machine-report／design-training）、待核准×2（guide-app／test-baton-pickup-0706）、done×2（o4-soundtrack／session-gate-fix）、提名×5——仍 0 個「待規劃」/「active」整欄精確相等項，今晚循環棒預期秒退。
**待核准/提名清單**：待核准×2——20260706-guide-app（主題方向已裁A，剩氛圍底圖/縮圖風格待重拍裁決＋anchor升級提案待裁決）、test-baton-pickup-0706（backlog全勾，建議直接結案）；提名×5——ody-evidence-gate／southlibrary-fonts／cowork-c-tasks／sreclaim-verify-b／pptmap-skill（皆待核准轉「待規劃」啟動，後4項另需補掛對應repo）。
**blockers待決**（逾期天數，自07-21首次卡住算至今日08-12）：
- machine-report修正意見：**已逾期22天**（07-21起無回覆，o4-soundtrack已於08-11解決，此為僅剩同批舊卡點）
- guide-app anchor升級提案：**已逾期22天**（07-21起無回覆；主題方向裁決已於08-11另案解決，不影響此項）
**產能算術**：active mission數＝0 → 無backlog可推進，無法推估完成日；解法唯一：裁決任一卡點才有下一棒可作項（或核准 guide-app/test-baton 待核准項、或核准提名轉待規劃）。
**合併建議（收貨＝以下指令）**：`git fetch origin && git checkout main && git merge origin/night-relay --no-edit && git push origin main`（main 端 QUEUE.md 已數週未同步 night-relay 狀態，建議儘快收貨一次以避免下次再發生同型三檔衝突）。

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
