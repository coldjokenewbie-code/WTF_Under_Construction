# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**提醒棒 2026-07-29 19:00**：main 已無未併入項（night-relay 領先 main 557 commits，0 落後，晨報棒已同步）。QUEUE 仍無「待規劃」/「active」整欄精確相等項（現況：parked×3／待核准×2／done×1／提名×5），今晚 19:30/21:30/23:30/01:30 四棒預期全數秒退——連續第7晚同因。
**產能算術（義務）**：0 個 active mission，今晚排定4棒，以「每棒一項」估算＝0 項可完成，**無預計完成日**（無案可推進，非額度或效率問題，是待使用者裁決卡住）。三個受阻案剩餘 backlog：guide-app 6/19 未勾（卡 anchor 升級提案裁決）、machine-report 3/13 未勾（待補具體修正意見）、o4-soundtrack 5/10 未勾（討論閘未拍板）。
**待核准清單（2項，未變）**：guide-app（anchor 升級提案待裁決）／test-baton-pickup-0706（backlog 全勾4/4，建議直接結案改done，無需續跑）。
**提名清單（5項，未變，掛載不足未轉待規劃）**：ody-evidence-gate／southlibrary-fonts（需掛SouthLibrary）／cowork-c-tasks（需掛cowork_CDIC）／sreclaim-verify-b（需掛S-reclaimed-water-plant）／pptmap-skill（需掛ppt_map_mark）。
**Blockers 待決**：o4-soundtrack 方向裁決（路線二拍板 vs 硬底線4修訂提案）**已逾期7天**（使用者07-21告知07-22回覆，至今未見）；machine-report 待補具體修正意見；guide-app anchor 升級提案待裁決；design-training 本週雲端無可作項（非卡點）。

## 佇列

| slug | 狀態 | 優先序(1最高) | 一句話方向 |
|---|---|---|---|
| 20260706-machine-report | parked | 1 | 互動機具設計報告書（億元標案等級）；**2026-07-21 使用者驗收未過，暫時擱置**，待使用者補充具體修正意見（見 _blockers.md），補充後改回待核准/active |
| 20260706-guide-app | 待核准 | 2 | 【2026-07-08 改向】優化現有 app（Assembly_Plant_Mobile_Guide，分支 ui-uplift）：M2 界達成（增量一～八，audit #6/#7 全數完成）。**2026-07-21 使用者已裁決風格方向（工業風/暗色為主/禁可愛風,icon尤其注意）**，剩餘唯一卡點：anchor 升級提案待使用者裁決，見 backlog/_blockers |
| 20260706-o4-soundtrack | parked | 3 | O4 配樂重做：先研究→使用者討論→才製作（討論閘未開前音樂增量一律 blocker）；語音剪接/畫面品質方向已獲使用者認可；**23:34 棒觸發停止閘（連續2棒零進展）**，卡點見 _blockers.md，**2026-07-21 使用者告知方向拍板明日(07-22)回覆** |
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
