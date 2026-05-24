---
name: ai-team
description: 動態 Tech Lead 協作框架。依使用者指派決定指揮層（Tech Lead），設定執行層角色邊界與任務生命週期。
---

# AI Team — 動態 Tech Lead 模式

## 啟動時機

收到「/ai-team」或明確需要下派 Agent 執行任務時載入。

---

## 核心角色與動態委派

**Tech Lead (Orchestrator)**：動態指派之指揮角色。預設為 User 自己，或由 User 於對話開始時輸入 `Appoint [AgentName] as Tech Lead`（例如 `指派 Antigravity 擔任 Tech Lead`）指派特定 AI（如 Antigravity、Codex、Claude）擔任。負責任務分析、協調、撰寫 `AGENT_SPEC` 以及最終驗收。

**Execution Agents (執行層)**：所有未被指派為 Tech Lead 的 AI（包含被降級為執行層工具的 Claude Code、Antigravity、Codex）。在 Tech Lead 給定的 Scope 內執行實作細節，嚴格受 Spec 約束，不得擅自超出 scope。

---

## 任務生命週期

```
收到需求
    │
    ▼
[Tech Lead] 需求分析 → 評估影響範圍 → 決定執行路徑
    │
    ├── 架構/資料/跨檔/診斷類 ──► Tech Lead 自行執行（或由 PO 親自執行）
    │
    └── 純視覺/單一元件/明確 scope ──► 撰寫 AGENT_SPEC → 下派 Execution Agent
                                               │
                                               ▼
                                       [Execution Agent] 執行
                                       完成後回傳 handoff report
                                               │
                                               ▼
                                       [Tech Lead] 驗收審查
                                       確認無 scope 蔓延
                                               │
                                     PASS ──► commit & 通知 PO
                                     FAIL ──► Tech Lead 退回或接手修正
```

---

## 任務類型速查

| 問題 | → |
|---|---|
| 需要讀懂業務邏輯才能做對？ | Tech Lead 自行執行（或由 PO 親自執行） |
| 影響超過 3 個檔案？ | Tech Lead 自行執行（或由 PO 親自執行） |
| 會改到 types / data？ | Tech Lead 自行執行（或由 PO 親自執行） |
| 純視覺，有明確參照可以複製？ | 可下派 Execution Agent |
| 單一元件，scope 清楚？ | 可下派 Execution Agent |

猶豫時，預設由 Tech Lead 執行。

---

## 下派 Execution Agent

使用 `AGENT_SPEC_TEMPLATE.md` 建立任務規格。每份 AGENT_SPEC 必須包含：

- **任務說明**（1-2 句，說什麼不說為什麼）
- **Scope**（明確列出允許修改的檔案）
- **禁止修改**（預設：types.ts、data/*.ts、CSS 變數、路由、config）
- **設計系統約束**（背景色、強調色、字型、panel 樣式）
- **參照元件**（給 Agent 「看這個來做」的參照）
- **預期產出 checklist**

**Session 開始時啟動一次全域 Monitor（persistent）：**

```bash
tail -n 0 -f AGENT_SIGNAL.log | grep --line-buffered -E "DONE|ANALYSIS|DISCUSSION|QUESTION|FAIL|ERROR"
```

不需每次派任務重新啟動。Agents 只要寫入 AGENT_SIGNAL.log，Tech Lead 就會自動收到通知。

**派發時只需寫入 REQUEST 信號：**

```bash
echo "REQUEST|<AgentID>|<spec_path>|$(date -Iseconds)" >> AGENT_SIGNAL.log
```

Monitor 偵測到 `DONE` 信號後自動進入驗收。整個週期不需使用者手動觸發。

---

## 運作守則

**不中途確認**：Tech Lead 自主執行到階段完成，模糊決策自行預設，統一製作 HANDOFF 讓使用者一次審核，不中途詢問。

**Agent = 執行層（被降級之 Claude Code、Antigravity、Codex）**：透過 `AGENT_SPEC` + `AGENT_SIGNAL.log` 協作。

**Monitor 不是 loop**：等待 Agent 信號用 Monitor（事件驅動），偵測到 `AGENT_SIGNAL.log` 有新內容即自動接手驗收，不用輪詢。

---

## 驗收審查

收到 Agent 的 handoff report 後，Tech Lead 確認：

1. diff 是否只改了 Scope 內的檔案
2. 有無引入新的設計語言或 pattern
3. TypeScript 是否無編譯錯誤
4. 「待確認」項目是否需要 Tech Lead 決定後再繼續

## 任務結束清理

所有任務 VERIFIED PASS 後，執行清理：

```bash
rm -f _context/MONITOR_INSTRUCTION_codex.md
rm -f _context/MONITOR_INSTRUCTION_gemini.md
```

清理後 Agents 下次 session 不再自動監控（沒有任務時不應持續運行）。
新的 ai-team 任務開始時，重新建立 MONITOR_INSTRUCTION 檔案。

---

## 範本使用慣例

skill 目錄內含三個範本檔（`_TEMPLATE`）：
- `AI_TEAM_DIVISION_TEMPLATE.md`
- `AI_TEAM_WORKFLOW_TEMPLATE.md`
- `AGENT_SPEC_TEMPLATE.md`

Tech Lead 為專案撰寫實際文件時，**建立去除 `_TEMPLATE` 的新檔案**（如 `AI_TEAM_DIVISION.md`），
範本保持不動，以此區隔範本與專案特定文件。
