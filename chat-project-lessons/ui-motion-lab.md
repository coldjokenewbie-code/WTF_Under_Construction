# ui-motion-lab — Chat 專案知識庫

> 由 `/lesson-add 專案 chat ui-motion-lab` 維護。

## PRD v1

**定位**：展場互動 UI 動態設計工具。單一 HTML 檔，純前端，無伺服器。

### 核心工作流
```
使用者給 GIF → Claude 分析 → 輸出 atom JSON
→ 貼入 Motion Lab Import → bezier 微調
→ Export JSON → 貼回 Claude → 再調 → 迭代
```

### Atom 系統
6 個可獨立開關的動態單元，每個有 `enabled / from / to / curve[4]`：
`translateY` `translateX` `scale` `rotateZ` `opacity` `blur`

### 標準 JSON 格式
```json
{
  "name": "spring-enter",
  "duration": 600,
  "atoms": {
    "translateY": { "enabled": true,  "from": 40,  "to": 0,   "curve": [0.34, 1.56, 0.64, 1.0] },
    "scale":      { "enabled": true,  "from": 0.88,"to": 1.0, "curve": [0.34, 1.56, 0.64, 1.0] },
    "opacity":    { "enabled": true,  "from": 0,   "to": 1,   "curve": [0.25, 0.10, 0.25, 1.0] }
  }
}
```
未出現的 atom key → 保留現有值不覆蓋。
Curve 格式：CSS `cubic-bezier(x1,y1,x2,y2)`，y 值允許超出 0–1（overshoot）。

### Claude 的工作
- 收到 GIF → 分析動態 → 拆解成上述 JSON 輸出
- 收到 Export JSON → 調整參數後回傳新 JSON
- **不寫 app 程式碼**，除非使用者明確要求

### 現有檔案
`motion-lab-v2.html`：Atom List、Bezier Editor、Preview、Reference Library、Import/Export

### 下一版候選
- 每個 atom 獨立 duration
- Multi-keyframe timeline

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
