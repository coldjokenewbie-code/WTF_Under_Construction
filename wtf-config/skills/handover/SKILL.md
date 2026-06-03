---
name: handover
description: 產出 TaskLog + Handover 交接文件，並輸出交接 prompt 供下個 agent 使用。
---

# Handover

session 結束時執行，自動產生交接文件並輸出交接 prompt。

## 觸發方式

`/handover [主題描述]`

範例：`/handover D區觸控導覽HTML`

## 執行步驟（不需逐步確認）

### Step 1 — 確認主題

- 若使用者呼叫時**有提供主題** → 記錄，進入 Step 2。
- 若使用者**未提供** → 詢問：「請說明本次交接的主題（例：D區觸控導覽、E區首頁動畫）。」

### Step 2 — 寫入 TaskLog

在 `_context/` 建立 `TaskLog_YYYY-MM-DD_[主題].md`（若已存在則更新）。

必含章節：

```
## 1. 本次完成項目
## 2. 未解決問題（依優先度 P0/P1/P2 標記）
## 3. 主要輸入檔案
## 4. 下一步建議
```

### Step 3 — 寫入 Handover 文件

在 `_context/` 建立 `Handover_YYYY-MM-DD_[主題].md`。

必含章節：

```
## 1. 現況摘要
## 2. 檔案位置
## 3. 緊急修復（若有 P0 問題，詳述症狀 + 已嘗試 + 建議修法）
## 4. 技術細節（架構、關鍵參數、顏色、座標等）
## 5. 後續待辦
```

### Step 4 — 輸出交接 prompt

直接在對話輸出以下格式的交接 prompt，供使用者複製給下個 agent：

---

```
## 交接 Prompt — [主題]（[日期]）

**專案**：[專案名稱與採購案號]
**交接文件**：`_context/Handover_YYYY-MM-DD_[主題].md`
**工作紀錄**：`_context/TaskLog_YYYY-MM-DD_[主題].md`

### 接手請先做
1. 讀取上方兩份文件了解現況
2. [若有 P0 問題，列出第一步驟]

### 目標
[下個 agent 需完成的具體任務]
```

---

## 重要限制

- 不執行 `/merge-main` 或 `/session-end`，這是獨立 skill。
- 若需要 commit + push，請另外執行 `/session-end`。
