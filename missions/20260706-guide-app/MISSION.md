# MISSION：guide-app（導覽 App 優化——2026-07-08 使用者改向）
> 改向紀錄：原任務（開場頁/三視圖**原型**，對標錨-P1/P3/P4）已於 M1 交付並收貨，原 M2/M3 原型線**停止**。
> 新方向由使用者 2026-07-08 00:40 下達：優化**現有 app**（repo `Assembly_Plant_Mobile_Guide`），開分支做，先研究分析應改善哪些，再優化。

## 方向（一句話）
在 `Assembly_Plant_Mobile_Guide` repo 開分支 **`ui-uplift`**，先產出研究分析（應改善清單），再逐項優化——重點：**整體視覺、UI 整合（一致性）、加入動態**。

## 對象與環境
- 目標 repo：`Assembly_Plant_Mobile_Guide`（雲端已掛循環棒 trigger；主 session clone 在 `/workspace/assembly_plant_mobile_guide`）。
- 技術棧：Vite + React 19 + react-router 7 + framer-motion（已裝）+ Playwright（已配置）。手機導覽 app（mobile-first，驗收視窗 390×844）。
- 工作分支：`ui-uplift`（自 main 建）。**禁推 main**；成果在分支上累積，使用者驗後自併。

## 品質判定（anchors 鐵律）
- 一律 `wtf-config/anchors/README.md`：Playwright 截圖 vs `anchors/展示頁面.md` 錨點並列比較句，四級等第，禁自評分數、禁百分制。
- 已收貨的開場頁原型（`outputs/開場頁原型_20260707/`）＝視覺方向正錨，優化後的 app 要與它同一語彙。
- 動態/手勢類改動：無頭測試只算煙霧測試，一律標「待實機驗」。

## 硬底線
1. 分析先行：改善清單未產出前不動 code；清單每項附「現況截圖證據＋改了會好在哪」。
2. 優化分兩類：**低品味風險項**（一致性修整、間距/層級系統化、轉場與微互動動態、載入狀態）分析完可直接做；**高品味風險項**（配色重定調、版式大改、資訊架構變動）寫 `_blockers.md` 待使用者核准，不擅動。
3. 每輪改動後：`npm run lint`（tsc）零錯誤＋Playwright 煙霧測試通過＋改動頁前後截圖並列存 `out/`。
4. 不加新重量級依賴（動態用已裝的 framer-motion）；不改資料層語意。

## Milestone
1. `out/ui-audit_2026-07-08.md`：現況截圖全集＋應改善清單（分低/高品味風險、附優先序）→ 高風險項進 blockers，**低風險項不停等直接進 M2**。
2. 低品味風險項優化完成（分支 `ui-uplift`，含前後對照截圖＋煙霧測試證據）→ 待核准（使用者驗貨＋裁決高風險項）。
3. （使用者核准後）高品味風險項實施 → done。
