# MS Office 自動化流程 — Chat 專案知識庫

> 由 `/lesson-add 專案 chat MS Office 自動化流程` 維護。

## 專案背景

Power Apps + SharePoint 為主的 MS Office 自動化流程開發。

## 慣例與限制

- 響應式模式下容器定位限制（見 Lessons）
- SharePoint List 日期格式需特別處理（見 Lessons）

---

## 累積 Lessons

<!-- lessons-start -->
**[2026-04-09] Power Apps 響應式容器定位**
響應式模式下，容器位置不能用 X/Y，必須靠父容器的 LayoutAlignItems + LayoutJustifyContent 置中。
來源：PopupContainer 位置跑掉，反覆修正。

**[2026-04-09] 尺寸一律用比例**
所有寬高一律用 Parent.Width / Parent.Height 比例，禁止給固定值，否則換裝置會壞。
來源：Label Width 寫死後在不同裝置失效，來回修正兩次。

**[2026-04-09] SharePoint List 日期格式**
SharePoint List 的日期欄位預設格式為 yyyy/m/d（不補零），Filter 用 `Text(Today(), "yyyy/m/d")` 才能比對到。
來源：DateString 比對失敗，資料沒有顯示。
<!-- lessons-end -->
