# AI 團隊分工定義
> 版本：v2.0 — 2026-05 (動態 Tech Lead 升級版)

---

## 角色定義

### AI Tech Lead (Orchestrator / 指揮層)
負責「決定什麼要做、為什麼這樣做」，並對最終品質負責。  
由使用者動態指派（預設為使用者自己，或於開場委派特定 AI 擔任）。
持有完整 codebase 讀寫權限，負責編寫 `AGENT_SPEC` 與代碼驗收。

### Execution Agents (執行層)
負責「怎麼做」的實作細節，在 Tech Lead 給定的 scope 內執行。  
包括未被指派為 Tech Lead 的所有 AI（如被降級之 Claude Code、Antigravity、Codex）。
不做獨立判斷，有疑問時擱置並回報，嚴格受 Spec 約束。

---

## 分工矩陣

| 任務類型 | 執行方 | 原則 |
|---|---|---|
| 架構決策（資料結構、路由、型別定義） | Tech Lead | 影響全局，不可下放 |
| `types.ts`、介面定義 | Tech Lead | 牽一髮動全身 |
| 資料檔案（`data/*.ts`） | Tech Lead | 需領域知識驗證 |
| 跨多檔案的邏輯修改（>3 個檔案） | Tech Lead | 執行層 Agent 缺乏全局上下文 |
| Bug 診斷 | Tech Lead | 需讀懂根因，不只是症狀 |
| config / CLAUDE.md / AGENT_SPEC | Tech Lead | 定義執行層邊界，不可讓其自訂 |
| 驗收審查 | Tech Lead | 品質把關在 Tech Lead |
| 單一元件的 CSS / 視覺實作 | Execution Agent | 範圍明確，影響可隔離 |
| 新頁面範本（遵循既有 pattern） | Execution Agent | 有參照，複製延伸即可 |
| 純 HTML/CSS 靜態頁面 | Execution Agent | 無跨檔案邏輯 |
| 根據 Tech Lead 提供的資料填充 UI | Execution Agent | 資料由 Tech Lead 確認，Agent 只負責呈現 |

---

## Agent 授權邊界

### ✅ 可以做
- 修改或新增 CSS class
- 在現有設計系統內調整元件視覺
- 根據 spec 建立新元件（`.tsx`、`.css`）
- 填充 Tech Lead 提供的靜態資料進 UI
- 遵循既有 pattern 複製延伸
- 修改純 HTML/CSS 檔案

### ❌ 不可做（需回報 Tech Lead 決定）
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
| 2 | 資料內容錯誤（猜測名稱） | 資料任務下放給 Agent | 資料類一律由 Tech Lead 完成或提供完整清單 |
| 3 | Scope 蔓延（順手調整其他樣式） | 缺乏明確檔案邊界 | AGENT_SPEC 明列「本次只動這些檔案」 |
