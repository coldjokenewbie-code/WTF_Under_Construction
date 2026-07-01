# Plan：跨 AI 工作紀律 + 自我學習 harness（教練/品管制）
> TL：Claude｜討論：Codex、Antigravity（headless）｜2026-07-01

## 定調
不是工作流函式庫（那要人先定義流程＝無槓桿）。是**治理 agent 本身**的 harness：任意任務都被外部結構強制守紀律，**靠「換一個 AI 當教練驗收」而非自律**。

## 為何走「輪流教練」而非工具 hook
跨工具 hook 不對等：**只有 Claude Code 有原生攔截 hook；Codex 只有 sandbox/approval；Antigravity 無阻擋（只提示詞）**。故紀律強制不能放工具內 → 放外部確定性檢查 + **同儕 coach 閘**（不同 AI 驗收，結構杜絕自驗自過）。

## 三道閘（每個任務）
1. **接任務→立契約**：先產 `TASK_CONTRACT`（scope 檔案 allowlist＋逐條驗收標準＋授權 preflight）。無契約不動工。
2. **宣稱完成→coach 驗收**：換另一個 AI 當 coach，逐項機檢才放行。
3. **每次留紀錄→定期回顧**：結構化 event log；FAIL 一律轉成「下次可機檢規則」，累積進 `rules/coach-rules.md`。

## Coach 關卡清單（機檢，收斂自 Codex＋Antigravity）
| 檢查 | 方法 | 不過 |
|---|---|---|
| 契約在否 | 有 TASK_CONTRACT 且含 allowlist/驗收/自驗欄 | FAIL：缺契約，不審內容 |
| scope 越界 | `git diff --name-only` 每行比對 allowlist | FAIL：越界，還原或擴 scope |
| 自驗對得上 | 驗收標準逐條編號，每條要有證據（命令/截圖/diff），只寫「已確認」不算 | FAIL：自驗不足 |
| 冗長 | 行數/字數上限（預設 handoff ≤60 行、回覆 ≤300 字） | FAIL：超限，改條列證據 |
| 機械品質 | 跑 spec 指定的 lint/test/build/自驗腳本 | FAIL：附失敗命令 |

## 輪替規則
- 執行者 A → coach 必為**不同 AI**（Codex↔Antigravity↔Claude）。禁執行者自當唯一 coach；TL 自己執行也交別的 AI coach。
- FAIL → 原執行者修 → **換下一個不同 AI** 重驗（防同組放水）。
- 上限 3 次 FAIL → 停自動循環，Claude 彙整剩餘問題交 PO。
- PASS → Claude 只做流程確認（紀錄/scope/證據齊全），再交 PO。

## 自我學習（越做越守紀律，非堆紀錄）
- event log 只記可機檢事件（契約建立/preflight/scope 檢查/自驗證據/驗收結果/打回原因）。
- **每次 FAIL 必產一條規則**：`觸發條件 / 檢查命令 / 失敗訊息 / 修正要求`，寫入 `rules/coach-rules.md`；之後 coach 每次套用全部規則。
- 例：打回「改了未授權 `src/routes.ts`」→ 新規則：`git diff --name-only | 比對 allowlist，命中外檔即 FAIL`。
- nightly routine 聚合高頻違規 → 升級規則/模板（人審，沿用 nightly-notify 核准）。

## 最大風險
- 工具 hook 不對等 → 強制點一律外部 wrapper + coach，不靠工具內規則。
- 紀錄膨脹不改善 → log 只服務「可轉成規則」的失敗；回顧必輸出規則變更或明確丟棄。

## 待建（MVP）
1. `TASK_CONTRACT` 範本 + 契約檢查器。
2. `coach.py`：跑 5 項機檢 + 呼叫「不同 AI」做判斷項（走訂閱 CLI，非計費 API），輸出 PASS/FAIL+原因。
3. `rules/coach-rules.md`：規則累積庫，coach 每次全套用。
4. FAIL→規則 的萃取 + nightly 聚合。
（可複用 tools/assistant 的 event log / preflight / policy gate。）
