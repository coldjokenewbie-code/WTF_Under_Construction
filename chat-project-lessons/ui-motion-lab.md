# ui-motion-lab — Chat 專案知識庫

> 由 `/lesson-add 專案 chat ui-motion-lab` 維護。

## 專案背景

UI 動態設計工具，用於 motion atom 的燈箱參考、bezier 微調與 JSON 交換。

---

## 累積 Lessons

<!-- lessons-start -->
**[2026-04-09] 錄製功能定位：燈箱參考層，非分析工具**
錄製功能是「燈箱參考層」不是「分析工具」；動態拆解必須由 Claude 處理，app 只負責載入 JSON 結果。
來源：使用者誤以為 app 可自動分析錄製的 GIF 拆解 motion atom，釐清後確立工作流分工。

**[2026-04-09] 標準 atom JSON 雙向交換流程**
標準 atom JSON 格式已定義，Claude ↔ Motion Lab 雙向交換透過 Import/Export `{ }` 按鈕。
來源：建立 Import JSON → Load into Lab → bezier 微調 → Export → 再給 Claude 的完整迴圈。

**[2026-04-09] 本專案路徑**
本專案名稱為 `ui-motion-lab`，對應知識庫路徑 `chat-project-lessons/ui-motion-lab.md`。
<!-- lessons-end -->
