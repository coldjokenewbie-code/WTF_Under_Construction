# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**提醒棒 2026-07-09 17:06**｜night-relay 已併最新 main（含 07-09 guide-app 重驗＋制度層更新）。

**待核准清單**：①machine-report（優先1）M1+M2+M3 併案送審，內容全章＋opus 對抗審查已 PASS，待你核准改 done。②test-baton-pickup-0706（優先9）管線探針驗證通過、無實質產出，建議直接結案。

**active 產能算術**：guide-app 剩 7 項（M2 關卡前尚有 4 個可做項：讀碼修正/UI整合/動態/測試存證）；今晚 4 棒與 o4-soundtrack 輪替（約各 2 棒/晚），每棒一項估算約 2 晚後（07-11 前後）達 M2 待核准。o4-soundtrack 剩 4 項但全數卡在【討論閘】——方向二未拍板前，本機生成/接線/對抗審查 3 項皆無法推進，今晚可做項＝0，完成日待你拍板才能估算。

**blockers 待決**：guide-app＝暗色主題定調（A暗/B淺，推薦A）＋底圖風格統一，2 項附截圖。o4-soundtrack＝方向二拍板（卡生成）／本機執行生成腳本（憑證牆）／V2 文案「19世紀初期」應為1929待轉知英審。design-training（parked）＝WebFetch 全面403，4 選項待你擇一（見 `_blockers.md`）。

**提名候選（未啟動，需先改「待規劃」）**：ody-evidence-gate／southlibrary-fonts（需掛SouthLibrary）／cowork-c-tasks（需掛cowork_CDIC）／sreclaim-verify-b（需掛S-reclaimed-water-plant）／pptmap-skill。

**合併建議（收貨＝以下指令）**：
`git fetch origin && git checkout main && git merge origin/night-relay --no-edit && git push origin main`

## 佇列

| slug | 狀態 | 優先序(1最高) | 一句話方向 |
|---|---|---|---|
| 20260706-machine-report | 待核准 | 1 | 互動機具設計報告書（億元標案等級）；內容全章＋fresh-context 對抗審查(opus)PASS 已完成,M1+M2+M3 併案送審,待核准後改 done |
| 20260706-guide-app | active | 2 | 【2026-07-08 改向】優化現有 app（Assembly_Plant_Mobile_Guide，分支 ui-uplift）：先研究分析再優化——視覺/UI 整合/動態；MISSION 已改寫 |
| 20260706-o4-soundtrack | active | 3 | O4 配樂重做：先研究→使用者討論→才製作（討論閘未開前音樂增量一律 blocker）；語音剪接/畫面品質方向已獲使用者認可 |
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
