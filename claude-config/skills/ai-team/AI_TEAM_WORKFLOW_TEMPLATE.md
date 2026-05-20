# AI 團隊任務工作流
> 版本：v1.0 — 2026-04

---

## 任務生命週期

```
PO 下需求
    │
    ▼
[Claude] 需求分析
  • 釐清 what & why
  • 評估影響範圍
  • 決定執行路徑
    │
    ├── Claude 自行執行（架構/資料/跨檔/診斷類）
    │
    └── 下派 Agent（純視覺/單一元件）
          │
          ▼
    [Claude] 撰寫 AGENT_SPEC
      • 明確 scope（哪些檔案）
      • 設計系統約束
      • 預期 output checklist
          │
          ▼
    [Claude] 派發 + 啟動監控（自動，不等使用者）
      • 寫入 AGENT_SIGNAL.log：REQUEST|<agent>|<spec_path>|<ts>
      • 立即啟動 Monitor：
        tail -f AGENT_SIGNAL.log | grep --line-buffered "DONE|<AgentID>"
          │
          ▼
    [Agent] 執行
      • 收到 REQUEST 信號後讀取 spec 開始作業
      • 在 spec 內完成實作，有疑問擱置不自決
      • 完成後寫入 AGENT_SIGNAL.log：DONE|<AgentID>|<主檔案>|<ts>
          │
          ▼ Monitor 自動觸發
    [Claude] 驗收審查
      • Review diff
      • 確認無 scope 蔓延
      • 功能驗證
          │
     PASS ──► commit & 通知 PO
     FAIL ──► 修正後重驗 or Claude 接手
```

---

## Handoff 格式

### A. Claude → Agent（任務下派 + 自動監控）

使用 `AGENT_SPEC_TEMPLATE.md` 填寫。派發後**立即**執行以下兩步，不等使用者觸發：

```bash
# 步驟 1：寫入 REQUEST 信號（Agent 的 monitor 自動收到）
echo "REQUEST|<gemini/codex>|<spec_path>|$(date -Iseconds)" >> AGENT_SIGNAL.log

# 步驟 2：Claude 啟動 Monitor（自動等待完成）
# → 使用 Monitor tool，watching: DONE|<AgentID>
```

核心 AGENT_SPEC 區塊：

```markdown
## 任務說明
[1-2 句說明要做什麼，不說為什麼]

## Scope（只動這些檔案）
- `components/XxxComponent.tsx`
- `components/XxxComponent.css`

## 禁止修改
- `types.ts` 或任何型別定義
- `data/*.ts`
- CSS 變數（`--color-*` 等）
- Scope 以外的所有檔案

## 設計系統約束
- 背景色：`[#xxxxxx]`
- 強調色：`[#xxxxxx]`
- 字型：[主字型]（主）、[mono 字型]（mono）
- Panel 樣式：參照 `.[class-name]`

## 參照元件
- 結構參照：`components/ExistingComponent.tsx`
- 樣式參照：`index.css` 的 `.glass-panel`

## 預期產出
- [ ] [功能/視覺條件 1]
- [ ] [功能/視覺條件 2]
- [ ] TypeScript 編譯無錯誤

## 有疑問時
不要自行決定，列在回報的「待確認」區塊，Claude 來決定。
```

---

### B. Agent 完成信號（AGENT_SIGNAL.log）

Agent 完成後，**必須** append 一行：

```
DONE|<AgentID>|<修改的主檔案路徑>|<Timestamp>
```

範例：
```
DONE|Antigravity|output/B_HTML/css/B_style.css|2026-05-21T01:00:06+08:00
DONE|Codex|output/B_HTML/B_JS/B_app.js|2026-05-21T00:59:58+0800
```

Claude 的 Monitor（已在派發時自動啟動）偵測到信號後立即接手驗收，不需使用者通知。

---

### C. Agent → Claude（完成回報）

```markdown
## 完成回報

### 修改的檔案
- `components/XxxComponent.tsx`（新增）
- `components/XxxComponent.css`（新增）

### 做了什麼
[簡短說明，不超過 5 行]

### 驗證狀態
- [x] TypeScript 編譯通過
- [x] 視覺符合預期產出清單
- [ ] [未驗證的項目]

### 待確認（需 Claude 決定）
1. [疑問 1]
2. [疑問 2]

### 已知限制
- [限制說明]
```

---

## 驗收標準（自動化 — 待建立）

目前以人工確認替代，未來每個 Agent 任務應附帶測試腳本：

```
待建立：
- snapshot test：核心頁面視覺回歸
- interaction test：關鍵 CTA 可點擊、流程可走完
- mode test：各模式狀態（如 onsite / web）
```

---

## 任務類型判斷速查

| 收到需求後問自己 | 結論 |
|---|---|
| 需要讀懂業務邏輯才能做對？ | Claude 自行執行 |
| 影響超過 3 個檔案？ | Claude 自行執行 |
| 會改到 types / data？ | Claude 自行執行 |
| 純視覺，有明確參照可以複製？ | 可下派 Agent |
| 單一元件，scope 清楚？ | 可下派 Agent |
| 猶豫不決？ | 預設 Claude 執行 |

---

## 版本歷程

| 版本 | 日期 | 說明 |
|---|---|---|
| v1.0 | 2026-04 | 初版，基於 Assembly_Plant_Mobile_Guide 實戰經驗提煉 |
