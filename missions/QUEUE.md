# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**晨報棒 2026-09-20 08:30**：`git rev-list --count origin/main..origin/night-relay` = **1138**——**此數字異常，非昨夜產出，勿直接merge**。真實昨夜增量（昨08:30晨報基準31aff8d→今night-relay HEAD c5f0c09）僅5條，全為心跳/秒退（提醒棒19:00、19:33、21:30、23:30、01:32），零mission增量，連續64天零active。
**異常根因**：main最早commit僅到2026-08-31（共53條，多為另一套nightly LESSONS索引自動化直推main，與mission-loop無關）；night-relay仍存自2026-04-03起完整1190條歷史，兩者在此之前分屬不同commit鏈（如"Initial commit"在main端不可達）。裸比對把整段舊歷史誤算成「領先」。
**合併建議**：**不建議**執行`git merge origin/night-relay`到main——會拉入1138條舊/已被main壓縮取代的commit。請使用者先確認main是否曾被reset/squash（08-31前後），再決定night-relay要不要以main重新對齊。昨夜本身無實質內容可收貨。
**待核准清單**：20260706-guide-app（優先序2，anchor升級提案掛起→73天）／test-baton-pickup-0706（優先序9，backlog全勾，建議使用者直接結案）。
**blockers 待決**：無新增。machine-report 驗收未過待補修正意見（掛起→61天）；guide-app anchor升級提案待裁決（同上73天）。
**合併建議**：night-relay 目前無 main 未收之新 commit，本輪無需合併動作；今晚循環棒若有新增量，明早晨報棒會再給合併指令原文。

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
