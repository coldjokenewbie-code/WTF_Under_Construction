# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**提醒棒 2026-07-21 19:00**（實跑 20:16，排程延遲；後續使用者於對話中直接裁決數項，本段同步覆核最新狀態）。
**使用者今日裁決**：互動機具設計報告書驗收未過→改 `parked`，待補充具體修正意見／wtf-session-gate故障修復＋管線探針測試→核准為 `active`，但指定僅排 01:30 棒（午夜後）執行，19:30/21:30/23:30 棒跳過／存保O4開場影片配樂→方向拍板明日(07-22)回覆，維持 parked。
**待核准(1)**：導覽App優化(repo:Assembly_Plant_Mobile_Guide,P2,M2界達成增量一~八全勾,剩anchor升級提案+2項高品味主題裁決)
**active(2，僅限01:30棒執行)**：wtf-session-gate故障修復(WTF內部harness,P8)／管線探針測試(WTF內部機制測試,P9)
**parked(3，待裁決解封)**：互動機具設計報告書(repo:Aseembly_Plant_Interactive_machine,P1,使用者驗收未過待補充意見)／存保O4開場影片配樂(repo:claude_CDIC_O4,P3,方向拍板使用者明日回覆)／設計能力訓練(WTF內部常設任務,P4,卡WebFetch全面403,_blockers 4選項待裁決——今日已請使用者擇一，見對話)
**新 blockers**：互動機具設計報告書新增1條（待使用者補充修正意見）
**提名(5，未掛載/待啟動，同前)**：ody-evidence-gate／southlibrary-fonts／cowork-c-tasks／sreclaim-verify-b／pptmap-skill
**產能算術（義務）**：2 active，但皆限定 01:30 棒才可執行（19:30/21:30/23:34 三棒對這兩項需跳過，backlog 項數：session-gate-fix 3項／test-baton 1項）；以「每棒一項」推算，01:30 棒後兩項各需 1、3 棒才能做完，預計最快 07-22 完成 test-baton，session-gate-fix 預計 07-24 完成（皆以每日僅一次01:30棒可用計）。其餘 1 項待核准／3 項 parked 均卡使用者裁決，不計入算術。
**合併建議（收貨＝以下指令）**：
`git fetch origin && git checkout main && git merge origin/night-relay --no-edit && git push origin main`

## 佇列

| slug | 狀態 | 優先序(1最高) | 一句話方向 |
|---|---|---|---|
| 20260706-machine-report | parked | 1 | 互動機具設計報告書（億元標案等級）；**2026-07-21 使用者驗收未過，暫時擱置**，待使用者補充具體修正意見（見 _blockers.md），補充後改回待核准/active |
| 20260706-guide-app | 待核准 | 2 | 【2026-07-08 改向】優化現有 app（Assembly_Plant_Mobile_Guide，分支 ui-uplift）：M2 界達成（增量一～八，audit #6/#7 全數完成），剩餘低風險項卡 anchor 升級提案待裁決，見 backlog/_blockers |
| 20260706-o4-soundtrack | parked | 3 | O4 配樂重做：先研究→使用者討論→才製作（討論閘未開前音樂增量一律 blocker）；語音剪接/畫面品質方向已獲使用者認可；**23:34 棒觸發停止閘（連續2棒零進展）**，卡點見 _blockers.md，裁決後改回 active |
| 20260707-design-training | parked | 4 | 使用者設計能力訓練支援（常設,週循環）；**parked**:WebFetch 全面403(組織政策非暫時),案例包卡點連續2棒零進展,見 _blockers.md 4選項待裁決 |
| test-baton-pickup-0706 | active | 9 | 管線探針：23:34 棒驗證通過（三檔齊備＋成功推 night-relay），無實質產出,建議使用者直接結案。**2026-07-21 使用者核准，指定僅排 01:30 棒（午夜後）執行，19:30/21:30/23:30 棒跳過此項** |
| 20260721-session-gate-fix | active | 8 | 修 wtf-session-gate 故障：M1 止血（cmd_postread 補 exists 防禦）＋M2 根因（settings.json bundle SHA 納入 SSOT 自動同步＋四方機檢，不接線 PreToolUse/Stop）；規劃棒已產出 MISSION.md+backlog.md。**2026-07-21 使用者核准，指定僅排 01:30 棒（午夜後）執行，19:30/21:30/23:30 棒跳過此項** |
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
