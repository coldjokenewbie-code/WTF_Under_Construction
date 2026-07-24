# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**提醒棒 2026-07-24 19:00**：QUEUE 現況——**無 `待規劃`/`active` 項**，今晚 19:30/21:30/23:30/01:30 四棒依規將全數秒退（除非使用者本棒後核准新項）。
**待核准清單（2項，需使用者決策）**：
- **guide-app**：M2 界達成（增量一～八全勾），僅剩「anchor 升級提案」（字級收斂/元件一致性驗收標準）待裁決，2026-07-21 已提示、回覆仍待補。
- **test-baton-pickup-0706**：backlog 全勾（01:30 棒第3次機會成功觸發，證明管線可用），建議使用者直接改 `done` 或刪列結案，無需續跑。
**提名清單（5項，待核准後可轉「待規劃」）**：ody-evidence-gate／southlibrary-fonts／cowork-c-tasks／sreclaim-verify-b／pptmap-skill。
**parked 待決 blockers**：
- o4-soundtrack：配樂方向拍板（使用者告知 07-22 回覆，迄今未見更新）；另兩分支（sharp-gates-uebbk0／5zp0y5）待合併。
- machine-report：驗收未過，待使用者補充具體修正意見。
- design-training：使用者已裁決本機限定，非待決，僅本週雲端無可作項。
**產能算術**：0 個 active mission，剩餘 backlog 項數＝0；今晚排定 4 棒，若無新核准預計全數秒退，完成日不適用。使用者核准 guide-app／test-baton 或任一提名後，下一棒即可接手。
**合併建議（收貨＝以下指令）**：
`git fetch origin && git checkout main && git merge origin/night-relay --no-edit && git push origin main`

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
