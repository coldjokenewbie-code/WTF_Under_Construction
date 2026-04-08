# AI 團隊分工定義
> 版本：v1.0 — 2026-04

---

## 角色定義

### Claude — Tech Lead
負責「決定什麼要做、為什麼這樣做」，並對最終品質負責。  
不限工具使用，持有完整 codebase 讀寫權限。

### Antigravity Agent — 執行者
負責「怎麼做」的實作細節，在 Claude 給定的 scope 內執行。  
不做獨立判斷，有疑問時擱置並回報，不自行決定。

---

## 分工矩陣

| 任務類型 | 執行方 | 原則 |
|---|---|---|
| 架構決策（資料結構、路由、型別定義） | Claude | 影響全局，不可下放 |
| `types.ts`、介面定義 | Claude | 牽一髮動全身 |
| 資料檔案（`data/*.ts`） | Claude | 需領域知識驗證 |
| 跨多檔案的邏輯修改（>3 個檔案） | Claude | Agent 缺乏全局上下文 |
| Bug 診斷 | Claude | 需讀懂根因，不只是症狀 |
| config / CLAUDE.md / AGENT_SPEC | Claude | 定義 Agent 邊界，不可讓 Agent 自訂 |
| 驗收審查 | Claude | 品質把關在 Tech Lead |
| 單一元件的 CSS / 視覺實作 | Agent | 範圍明確，影響可隔離 |
| 新頁面模板（遵循既有 pattern） | Agent | 有參照，複製延伸即可 |
| 純 HTML/CSS 靜態頁面 | Agent | 無跨檔案邏輯 |
| 根據 Claude 提供的資料填充 UI | Agent | 資料由 Claude 確認，Agent 只負責呈現 |

---

## Agent 授權邊界

### ✅ 可以做
- 修改或新增 CSS class
- 在現有設計系統內調整元件視覺
- 根據 spec 建立新元件（`.tsx`、`.css`）
- 填充 Claude 提供的靜態資料進 UI
- 遵循既有 pattern 複製延伸
- 修改純 HTML/CSS 檔案

### ❌ 不可做（需回報 Claude 決定）
- 修改 `types.ts` 或任何 interface / type 定義
- 修改資料檔案（`data/*.ts`）
- 更動配色系統 / CSS 變數（`--color-*` 等）
- 安裝或移除 npm package
- 修改路由設定
- 建立新的設計語言（沒有參照的 UI 元素）
- 修改 `CLAUDE.md`、`AGENT_SPEC.md`、`settings.json`
- 在 scope 外主動優化或重構

---

## 常見踩坑與教訓

| # | 問題 | 根因 | 對策 |
|---|---|---|---|
| 1 | Agent 擅自改回舊主題 | spec 只說「要做什麼」，沒列禁止事項 | AGENT_SPEC 必須有明確「不可做」清單 |
| 2 | 資料內容錯誤（猜測展品名稱） | 資料任務下放給 Agent | 資料類一律由 Claude 完成或提供完整清單 |
| 3 | Scope 蔓延（順手調整其他樣式） | 缺乏明確檔案邊界 | AGENT_SPEC 明列「本次只動這些檔案」 |
