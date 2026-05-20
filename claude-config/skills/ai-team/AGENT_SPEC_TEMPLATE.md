# AGENT_SPEC — [任務名稱]
> 建立時間：YYYY-MM-DD  
> 建立者：Claude Tech Lead  
> 執行者：[Antigravity / Codex]

---

## 派發協議（Claude 填寫）

**REQUEST 信號**（Claude 寫入 `AGENT_SIGNAL.log`）：
```
REQUEST|[gemini/codex]|_context/AGENT_SPEC_[任務名稱].md|<Timestamp>
```

**Claude 監控指令**（派發後自動啟動）：
```bash
tail -f AGENT_SIGNAL.log | grep --line-buffered "DONE|[Antigravity/Codex]"
```

**Agent 完成信號**（Agent 寫入 `AGENT_SIGNAL.log`）：
```
DONE|[Antigravity/Codex]|[修改的主檔案路徑]|<Timestamp>
```

---

## 任務說明
<!-- 1-2 句說明要做什麼，不說為什麼。只描述行為，不解釋設計決策。-->

[任務說明]

---

## Scope（只動這些檔案）
<!-- 明確列出，Agent 不得修改 Scope 以外的任何檔案 -->

- `[檔案路徑 1]`
- `[檔案路徑 2]`

---

## 禁止修改

- `types.ts` 或任何型別定義
- `data/*.ts` 資料檔案
- CSS 變數（`--color-*`、`--bg`、`--panel` 等）
- 路由設定
- `CLAUDE.md`、`AGENT_SPEC.md`、`settings.json`
- Scope 以外的所有檔案

---

## 設計系統約束
<!-- 從專案的 design token 複製 -->

- 主題：[淺色 / 深色]
- 背景色：`[#xxxxxx]`
- 強調色：`[#xxxxxx]`
- 主字型：`[字型名稱]`
- Mono 字型：`[字型名稱]`
- Panel 樣式：參照 `[class 名稱]`

---

## 參照元件
<!-- Agent 應該「看這個來做」的參照，避免自行發明 pattern -->

- 結構參照：`[元件路徑]`
- 樣式參照：`[class 名稱 / 檔案路徑]`

---

## 預期產出

- [ ] [具體功能或視覺條件 1]
- [ ] [具體功能或視覺條件 2]
- [ ] TypeScript 編譯無錯誤
- [ ] 無修改 Scope 以外的檔案

---

## 有疑問時

**不要自行決定。**  
將疑問列在完成回報的「待確認」欄位，由 Claude 決定後再繼續。  
寧可擱置，不要猜測。

---

## 完成流程（Agent 執行）

1. 完成所有修改
2. 寫入 `AGENT_SIGNAL.log`（格式見上方派發協議）
3. **Claude 的 Monitor 收到信號後自動驗收**，不需另行通知

**有疑問時**：不要自行決定。列在 `AGENT_SIGNAL.log` 信號後另起一行：
```
QUESTION|[Antigravity/Codex]|[任務名稱]|<問題描述>|<Timestamp>
```

---

## 完成回報格式（Agent 填寫，寫入對應 RESPONSE 檔或直接附在信號後）

```
### 修改的檔案
- 

### 做了什麼
[簡短說明，不超過 5 行]

### 驗證狀態
- [ ] 編譯 / 語法檢查通過
- [ ] 視覺符合預期產出清單

### 待確認（需 Claude 決定）
1. 
2. 

### 已知限制
- 
```
