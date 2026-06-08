---
name: ai-team
description: 動態 Tech Lead 協作框架。依使用者指派決定指揮層（Tech Lead），設定執行層角色邊界與任務生命週期。
---

# AI Team — 動態 Tech Lead 模式

## 啟動時機

收到「/ai-team」或明確需要下派 Agent 執行任務時載入。

---

## 協作通道：同機優先用 headless CLI 直驅（信號檔為 fallback）

三個工具都有 headless CLI，**同一台機器上 Tech Lead 可直接用 Bash 同步呼叫其他工具**，即時拿回答，**不需** `AGENT_SIGNAL.log` 中繼、不需 `MONITOR_INSTRUCTION_*.md` 待辦、不需常駐 `tail -f` monitor：

| 工具 | headless 指令 |
|---|---|
| Claude | `claude -p "<prompt>"` |
| Codex | `codex exec "<prompt>"`（`-s read-only` 唯讀、`--skip-git-repo-check`） |
| Antigravity | `agy --print "<prompt>"` |

- 誰當 Tech Lead 都對稱：可直接 CLI 驅動其餘兩個（討論、派工、收驗一氣呵成）。
- **三者 headless 皆單次無狀態**（每次新 session）→ 多輪討論由 Tech Lead 每次把脈絡餵進 prompt。
- headless 慢/卡時：獨立前景跑、加 timeout，卡住即砍重跑，**不要無限等也不要跳過**（追原因：常見 GUI 同例鎖、MCP 連線）。
- **各 agent CLI 實戰規格**（登入、短 prompt、寫檔限制、signal 慣例）詳見 `<WTF_ROOT>/tools/ai-team/cli-reference.html`——加入 ai-team 時只讀自己 agent 的段落即可。

**信號檔機制（下方 AGENT_SIGNAL.log / MONITOR_INSTRUCTION）只在這些情況才用**：
1. **跨機**（Windows ↔ Mac）：bash 叫不到另一台 CLI。
2. **GUI 模式**：對方在 IDE 互動跑（非 headless），bash 搆不到。
3. 需要**持久化狀態**（誰說了什麼、待辦快照）跨 session 留存。

---

## 核心角色與動態委派

**Tech Lead (Orchestrator)**：動態指派之指揮角色。預設為 User 自己，或由 User 於對話開始時輸入 `Appoint [AgentName] as Tech Lead`（例如 `指派 Antigravity 擔任 Tech Lead`）指派特定 AI（如 Antigravity、Codex、Claude）擔任。負責任務分析、協調、撰寫 `AGENT_SPEC` 以及最終驗收。

**Execution Agents (執行層)**：所有未被指派為 Tech Lead 的 AI（包含被降級為執行層工具的 Claude Code、Antigravity、Codex）。在 Tech Lead 給定的 Scope 內執行實作細節，嚴格受 Spec 約束，不得擅自超出 scope。

---

## 強制協作協議（討論 → 共識 → 執行 → 輪流驗收）

> 此協議為 ai-team 的核心鐵則，任何任務一律依序執行，不得跳步。

### 1. 討論至少 3 輪
- 收到需求後，Tech Lead 與執行層 agents **至少討論 3 輪**才動工。
- 每輪由 Tech Lead 彙整脈絡（headless 單次無狀態，須每輪餵入前情），讓各 agent 提出方案／質疑／補強。
- 目的：在動工前把 scope、做法、風險、設計約束談清楚。

### 2. 有共識才執行
- 3 輪後若達成共識 → 進入執行。
- 若仍無共識 → 再加輪討論或交回 PO 裁示，**不得在分歧未解下動工**。

### 3. 輪流驗收（程式碼／邏輯層）
- 執行完成後進入驗收，**由各 agent 輪流擔任驗收者**（不是只有 Tech Lead 一人驗）。
- 驗收者提出問題 → 執行者調整 → 換下一位 agent 驗 → 再調整，循環直到通過。
- 重點：diff 是否只動 scope、有無引入新 pattern、邏輯／編譯正確性。

### 4. 輪流擷圖驗收（視覺層，最多 10 輪）
- 邏輯驗收通過後，進入**視覺擷圖驗收**：用 `/ui-review`（Playwright 無頭擷圖）出圖。
- 各 agent **輪流看圖驗收 → 指出問題 → 調整 → 再擷圖**，循環。
- **上限 10 輪**：到第 10 輪仍未收斂，停止自動循環、彙整剩餘問題交 PO 裁示，不無限打磨。

### 5.（選用）Webwright 自動化驗收
- 可選用 Microsoft Research 的 **Webwright** 做自動化網頁驗收，補強人工擷圖驗收（未驗證實際整合方式，採用前先確認可用）。

### 6. 驗收完交 PO，禁止自行 commit
- ai-team 全部驗收通過後，**提交給 PO（使用者）做最終驗收，不可自己 commit**。
- 由 PO 驗收通過後才 commit。

### 7. Tech Lead 自行執行也要讓小隊驗收
- 若 Tech Lead 判斷由自己執行（架構/資料/跨檔/診斷類），完成後**仍須交給執行層小隊輪流驗收**。
- **禁止自驗自過**——自己做的不可以自己當唯一驗收者。

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
                                       輪流驗收（程式碼 → 擷圖，見強制協作協議）
                                       各 agent 輪流驗，禁自驗自過
                                               │
                                     PASS ──► 交 PO 驗收（不自行 commit）
                                     FAIL ──► 退回調整、輪流重驗
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
