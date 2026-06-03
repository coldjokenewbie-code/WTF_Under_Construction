---
name: tasklog-naming
description: 工作紀錄檔名規則。AI 載入專案時必須遵循：只讀 TaskLog_ 開頭的檔案，跳過 ClosedTaskLog_ 開頭的檔案。
---

# 工作紀錄檔名規則

## 命名格式

工作紀錄檔案存放於 `_context/`，檔名前綴依工作狀態決定：

| 狀態 | 檔名前綴 | 位置 | 範例 |
|---|---|---|---|
| 進行中／未結案 | `TaskLog_` | `_context/` | `_context/TaskLog_2026-05-05_C區多媒體內容規劃.md` |
| 已結束／告一段落 | `ClosedTaskLog_` | `_context/archive/` | `_context/archive/ClosedTaskLog_2026-05-05_C區多媒體內容規劃.md` |

完整格式：`<前綴>YYYY-MM-DD_<主題>.md`

**結案 = 兩者都要**：改前綴 `TaskLog_`→`ClosedTaskLog_`，**並**移入 `_context/archive/`。

## AI 處理規則

### 強制規則：載入專案時

1. **必須讀取**：所有 `_context/TaskLog_*.md` 檔案
2. **必須跳過**：`_context/archive/` 整個資料夾，以及任何 `ClosedTaskLog_*.md`
3. **務必讀取**：`_context/lessons-learned.md`（所有跨工作教訓的彙整，永遠讀）
4. **讀取 Handover_ 後立即搬移**：見下方「Handover 接手規則」

### 為什麼跳過 ClosedTaskLog_

- 已結案的工作紀錄屬於「歷史檔案」，內容對當前任務無直接幫助。
- 跨工作的可重用知識應已彙整至 `lessons-learned.md`。
- 跳過已結案紀錄可節省 token、避免被舊脈絡干擾。

### 例外

僅當下列情境發生，AI 才可主動讀取 ClosedTaskLog_：
- 使用者明確指示「請參考 ClosedTaskLog_<某檔名>」
- 使用者要求「查詢過去某項工作做了什麼」
- 接手修改某個已結案工作的延伸需求（使用者明確點名該工作）

## Handover 接手規則

### 規則：讀取 Handover_ 檔 = 已接手，立即搬移

當 AI 讀取 `_context/Handover_*.md` 任意一份時，必須在讀取完成後立即執行：

1. 確認 `_context/archive/` 資料夾存在；若不存在則建立
2. 將該 Handover_ 檔移入 `_context/archive/`

```bash
# 建立資料夾（若不存在）
mkdir -p _context/archive

# 搬移檔案
mv "_context/Handover_2026-05-14_D區觸控導覽.md" "_context/archive/"
```

### 為什麼這樣做

- Handover_ 是「交接備忘」，接手後就完成使命，不需再被後續 agent 重複讀取。
- 留在 `_context/` 會讓每次開場掃描都讀到，浪費 token 且容易誤判為「待接手」狀態。
- 搬到 `_context/archive/`（與結案紀錄同處）而非刪除，保留歷史查詢的可能性。

### 例外

- 使用者明確說「不要搬移」或「先別動」時，跳過搬移動作。
- 讀取是為了「查詢過去交接記錄」（非接手）時，不搬移。

---

## 狀態轉換

### 何時改為 ClosedTaskLog_

工作達成下列任一條件時，使用者會通知 AI 改檔名：
- 已交付業主／客戶
- 工作目標達成且無預期後續變更
- 使用者明確說「告一段落」「結案」「收尾」

### 改檔名動作（改前綴 + 移 archive，一步到位）

```bash
mkdir -p _context/archive
# 進行中 → 結案：加 Closed 前綴並移入 archive/
mv "_context/TaskLog_2026-05-05_C區多媒體內容規劃.md" \
   "_context/archive/ClosedTaskLog_2026-05-05_C區多媒體內容規劃.md"
```

或使用檔案工具（Read/Write）：
1. 讀取原檔內容
2. 寫到 `_context/archive/ClosedTaskLog_<日期>_<主題>.md`
3. 刪除原 `_context/TaskLog_*` 檔（或請使用者手動刪）

## INDEX.md 與 TaskLog 分工（避免雙真相源）

`_context/INDEX.md` 與 `TaskLog_` 職責不同，**不可重複內容**：

| | INDEX.md | TaskLog_ |
|---|---|---|
| 數量 | 一個，常駐持續覆寫 | 多份，按主題/日期，會歸檔 |
| 角色 | 導航儀表板：現況一句話 ＋ **指向**最新 TaskLog/Handover 的連結 ＋ 關鍵檔位置 | 單一工作線的過程紀錄：完成項、未解決、下一步 |

**鐵律：todo／進度的唯一真相源＝當前 `TaskLog_`。INDEX 只放連結與現況快照，不複製 todo 細節。**
- INDEX 若開始列詳細待辦＝雙真相源，必然漂移（INDEX 落後現實）。發現即收斂回 TaskLog，INDEX 改放連結。
- 進場順序：先讀 INDEX 掌握「現在在哪、最新 TaskLog 是哪份」→ 再讀該 TaskLog 拿細節。
- 例外：少數「待用戶拍板的決策閘」屬儀表板層級，可在 INDEX 以短清單列出（非工作線 todo）。

## 相關規則
- `thumbnail-aware-images`（縮圖規則 skill）
