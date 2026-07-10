# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**提醒棒 2026-07-10 17:00**
**待核准清單**：①machine-report（M1+M2+M3 併案送審，全章＋對抗審查 opus PASS，建議直接核准）②test-baton-pickup-0706（管線探針驗證通過，無實質產出，建議直接結案）。
**提名清單**（5 項，皆待掛載對應 repo，見 mission-loop.md 第 6 節）：ody-evidence-gate／southlibrary-fonts／cowork-c-tasks／sreclaim-verify-b／pptmap-skill。
**blockers 待決**：
- guide-app（4 條）：①暗色 vs 淺色主題定調（推薦 A 暗色）②展品縮圖/氛圍底圖風格統一路線③定錨棒提案——前後截圖硬底線升級為與展示頁面.md 錨點並列比較句，是否採納？④MISSION.md 正錨路徑訂正（低優先非阻塞）。
- o4-soundtrack（3 條）：①【討論閘】方向二拍板（生成音檔前必要，核心卡點）②拍板後需你本機跑生成腳本③V2 文案「19世紀初期」誤植待轉知英審。
- design-training：parked，4 選項待裁決（WebFetch 組織政策 403，判定非暫時性）。
- machine-report：milestone 回溯簽核 3 選項待裁決（不阻塞，已繼續推進）。
**產能算術**：
- guide-app（active）：backlog 剩 4 個具體增量到 M2 界（間距系統化／字級收斂／元件一致性／動態微互動），今晚排定 4 棒（19:30/21:30/23:30/01:30）；o4-soundtrack 可作項＝0 故全數輪替回本案，以一棒一項推算，**預計今晚即可抵達 M2 界**，之後停等你核准。
- o4-soundtrack（active）：剩 4 項全卡拍板/本機執行，今晚可作項＝0，預計持續空轉至你拍板方向二為止。
**合併建議（收貨＝以下指令）**：
`git fetch origin && git checkout main && git merge origin/night-relay --no-edit && git push origin main`

## 佇列

| slug | 狀態 | 優先序(1最高) | 一句話方向 |
|---|---|---|---|
| 20260706-machine-report | 待核准 | 1 | 互動機具設計報告書（億元標案等級）；內容全章＋fresh-context 對抗審查(opus)PASS 已完成,M1+M2+M3 併案送審,待核准後改 done |
| 20260706-guide-app | 待核准 | 2 | 【2026-07-08 改向】優化現有 app（Assembly_Plant_Mobile_Guide，分支 ui-uplift）：M2 界達成（增量一～八，audit #6/#7 全數完成），剩餘低風險項卡 anchor 升級提案待裁決，見 backlog/_blockers |
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
