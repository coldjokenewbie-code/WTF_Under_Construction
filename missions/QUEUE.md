# Mission 佇列（雲端自主迴圈唯一入口）
> 規格見 `wtf-config/playbooks/mission-loop.md`。使用者加一行＝派工；把「待核准」改「active」＝核准。
> 狀態機：待規劃 → 待核准 → active → done；旁路 parked（零進展/偏航，待使用者處置）。

## 今日快報
（由 17:00 提醒棒自動覆蓋更新）

## 佇列

| slug | 狀態 | 優先序(1最高) | 一句話方向 |
|---|---|---|---|
| test-baton-pickup-0706 | 待規劃 | 1 | 驗證循環棒接棒：建 MISSION＋寫 journal＋推 night-relay 即算成功（一棒內完成） |
| ody-evidence-gate | 提名 | 2 | tools/ody 加機檢規則：宣稱「已完成」無驗證證據→攔截，附 pytest（WTF 內，可立即跑） |
| southlibrary-fonts | 提名 | 3 | Google Fonts 改本地 @font-face 去 CDN 依賴（需先到 Routines UI 給循環棒補掛 SouthLibrary repo） |
| cowork-c-tasks | 提名 | 4 | C 區 5 任務 docx 文案轉 TASKS 陣列寫入 C.html（需先補掛 cowork_CDIC repo） |
| sreclaim-verify-b | 提名 | 5 | 100 句查證批次 B 補 A 級一手來源（需先補掛 S-reclaimed-water-plant repo） |
| pptmap-skill | 提名 | 6 | 拉線標註流程封裝成可重用 skill（需先補掛 ppt_map_mark repo） |

> 「提名」＝選題官提的候選，棒子不會碰；你把狀態改成「待規劃」即啟動該項。

## 使用說明（給使用者）
- **派新工作**：加一行，狀態填「待規劃」。當晚 19:00 起循環棒會先跑規劃棒，產出 MISSION 後停下等你核准。
- **核准**：把該行狀態改成「active」（手機上跟任何 Claude session 說也行）。
- **暫停**：改「parked」；**調順序**：改優先序數字。
- 卡點決策看各 mission 資料夾的 `_blockers.md`；17:00 快報會彙整。
