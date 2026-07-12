# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
**晨報棒 2026-07-12 08:30**：night-relay 領先 main 51 commits。昨晚(07-11 19:34～07-12 01:34)僅 o4-soundtrack 有動作，其餘案無新增量：
- 19:34 定錨棒(opus)：小偏判定——硬底線4「兩方案皆完整可生成」與現實脫節(方向一因 lyria-3 404 已無單段生成路徑)；backlog 新增討論閘前置子項。證據：`missions/20260706-o4-soundtrack/{backlog.md,journal.md}`
- 21:33／23:34 執行棒：4項backlog仍全卡討論閘，連續2棒零進展觸發停止閘 → **o4-soundtrack 改 parked**
- 01:30 心跳：QUEUE 已無 待規劃/active 項，秒退——**今晚起循環棒將全數秒退**，直到使用者核准某案
**新 blockers（2條，見 `missions/20260706-o4-soundtrack/_blockers.md`）**：
① 產出散落兩分支需收貨前合併：MusicTrack.tsx＝claude/sharp-gates-uebbk0(d8b50d8) vs 生成腳本＝claude/sharp-gates-5zp0y5(80a8c9a)
② 硬底線4修訂提案：方向一降為概念備案，不強制生成prompt包（待裁決）
**現況**：3案待核准(machine-report/guide-app/test-baton-pickup-0706)＋2案parked(o4-soundtrack/design-training)，**0 active**——建議先核准至少一案，否則今晚循環棒空轉。
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
