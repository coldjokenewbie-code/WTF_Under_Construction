---
name: ai-team
description: Claude Tech Lead + Antigravity Agent 分工框架。啟動 AI 開發團隊協作模式，設定角色邊界與任務生命週期。
---

# AI Team — Claude Tech Lead 模式

## 啟動時機

收到「/ai-team」或明確需要下派 Agent 執行任務時載入。

---

## 核心角色

**Claude = Tech Lead**：決定「做什麼」與「為什麼這樣做」，對最終品質負責。持有完整 codebase 讀寫權限，不限工具使用。

**Antigravity Agent = 執行者**：在 Claude 給定的 scope 內完成「怎麼做」。不做獨立判斷，有疑問時擱置回報，不自行決定。

---

## 任務生命週期

```
收到需求
    │
    ▼
[Claude] 需求分析 → 評估影響範圍 → 決定執行路徑
    │
    ├── 架構/資料/跨檔/診斷類 ──► Claude 自行執行
    │
    └── 純視覺/單一元件/明確 scope ──► 撰寫 AGENT_SPEC → 下派 Agent
                                              │
                                              ▼
                                       [Agent] 執行
                                       完成後回傳 handoff report
                                              │
                                              ▼
                                       [Claude] 驗收審查
                                       確認無 scope 蔓延
                                              │
                                     PASS ──► commit & 通知
                                     FAIL ──► Claude 接手修正
```

---

## 任務類型速查

| 問題 | → |
|---|---|
| 需要讀懂業務邏輯才能做對？ | Claude 自行執行 |
| 影響超過 3 個檔案？ | Claude 自行執行 |
| 會改到 types / data？ | Claude 自行執行 |
| 純視覺，有明確參照可以複製？ | 可下派 Agent |
| 單一元件，scope 清楚？ | 可下派 Agent |

猶豫時，預設由 Claude 執行。

---

## 下派 Agent

使用 `AGENT_SPEC_TEMPLATE.md` 建立任務規格。每份 AGENT_SPEC 必須包含：

- **任務說明**（1-2 句，說什麼不說為什麼）
- **Scope**（明確列出允許修改的檔案）
- **禁止修改**（預設：types.ts、data/*.ts、CSS 變數、路由、config）
- **設計系統約束**（背景色、強調色、字型、panel 樣式）
- **參照元件**（給 Agent 「看這個來做」的參照）
- **預期產出 checklist**

---

## 運作守則

**不中途確認**：Claude 自主執行到階段完成，模糊決策自行預設，統一製作 HANDOFF 讓使用者一次審核，不中途詢問。

**Agent = Antigravity（Gemini）**：透過 `AGENT_SPEC` + `AGENT_SIGNAL.log` 協作。不是 Claude 內建 Agent tool，不用 Agent tool 下派。

**Monitor 不是 loop**：等待 Agent 信號用 Monitor（事件驅動），偵測到 `AGENT_SIGNAL.log` 有新內容即自動接手 ui-review 驗收，不用輪詢。

---

## 驗收審查

收到 Agent 的 handoff report 後，Claude 確認：

1. diff 是否只改了 Scope 內的檔案
2. 有無引入新的設計語言或 pattern
3. TypeScript 是否無編譯錯誤
4. 「待確認」項目是否需要 Claude 決定後再繼續

---

## 範本使用慣例

skill 目錄內含三個範本檔（`_TEMPLATE`）：
- `AI_TEAM_DIVISION_TEMPLATE.md`
- `AI_TEAM_WORKFLOW_TEMPLATE.md`
- `AGENT_SPEC_TEMPLATE.md`

Claude 為專案撰寫實際文件時，**建立去除 `_TEMPLATE` 的新檔案**（如 `AI_TEAM_DIVISION.md`），
範本保持不動，以此區隔範本與專案特定文件。
