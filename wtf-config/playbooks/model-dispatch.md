# 模型調度守則
> 適用：Claude Code（含 web/remote）。Codex／Antigravity 跨工具派工另見 `skills/ai-team`、`tools/ody`
> 目的：主對話（指揮官）的 context 與額度只花在判斷上，粗活派便宜 subagent
> 觸發時機：任何任務動手前先過「派工判斷」；不確定就查本檔，不憑感覺

## 0. 型號與參數（2026-07-03 查證值，會過時）

**查證方式**：以下值查證自 2026-07-03 的 Claude Code remote 環境。型號會更新，**引用前先驗證**：問 `claude-code-guide` subagent「目前可用模型與 ID」，或看 `/model` 選單。**禁止憑訓練記憶填型號**；查不到的欄位寫「待使用者填」。

| 用途代號 | 模型名 | model ID（API 用） | Agent tool `model` 參數值 |
|---|---|---|---|
| 高階判斷 | Opus 4.8 | `claude-opus-4-8` | `opus` |
| 標準執行 | Sonnet 5 | `claude-sonnet-5` | `sonnet` |
| 廉價批次 | Haiku 4.5 | `claude-haiku-4-5-20251001` | `haiku` |
| （已不可得） | Fable 5 | `claude-fable-5` | `fable`——僅該次特殊 session 有，日常勿指定 |

**派工模型政策（2026-07-25 使用者裁定）**：預設派工一律 `opus`，不再以成本為優先考量；例外僅兩類——(a) 任務明確綁定 Fable 5 該次特殊 session／使用者指名 Fable 5；(b) 大量機械重複操作（見第 4 節）。舊「便宜優先、逐級升級」的成本優化邏輯全面讓位給此政策，第 4／5 節已依此改寫。

**額度緊縮備援（2026-07-08 查證，僅在 opus 因額度失敗時適用）**：
- 排程 Routine 的 fresh session 主模型＝建 Routine 時在 Routines UI 的 model selector 所選（官方文件 code.claude.com/docs/en/routines.md，2026-07-08 經 claude-code-guide 查證）；MCP 的 create/update_trigger **無 model 欄位**，改模型只能使用者進 claude.ai/code → Routines → Edit。
- 額度打頂時排程 session 是否自動 fallback：**查無官方文件**——夜鏈集體沉默時先懷疑打頂（呼應 mission-loop 誠實條款）。
- 派 `opus` 若因額度失敗→降 `sonnet` 續跑並記 journal，不停等；不因此改變預設政策。

**effort（推理力度）**：2026-07-03 查證——Claude Code 的 Agent tool **沒有逐次呼叫的 effort 參數**；effort 來自 subagent 定義檔（`.claude/agents/*.md` frontmatter）或 session 設定。Workflow 工具的 `agent()` 才有 `opts.effort`（`low`/`medium`/`high`/`xhigh`/`max`）。你的本機 CLI 版本可能不同，用前以 claude-code-guide 查證當下版本行為。

**額度歸屬**（未確認）：「被安全機制導向 Opus 4.8 的請求是否消耗原模型額度」查不到官方說法，建議到 claude.ai 的 usage 儀表板實測後把結論補進本節。

## 1. 指揮官不下場（派工判斷）

主對話動手前，對照三個門檻，**命中任一就派 subagent**：

| 門檻 | 派誰 | 例 |
|---|---|---|
| 預估閱讀 >300 行，或要開 >3 個檔 | Explore（搜尋）／general-purpose（要動手） | 「這個 bug 在哪」「整理所有用到 X 的地方」 |
| 「找找看」式搜尋（不確定在哪個檔） | Explore | 「哪裡定義了同步邏輯」 |
| 批次機械操作（改 N 個檔、跑 N 次驗證） | general-purpose，`model: haiku` 或 `sonnet` | 「把 12 個 SKILL.md 都加一行 frontmatter」 |

**不必派**（自己做反而省）：已知確切檔案位置的單點讀寫、單一命令執行、與使用者的對話判斷。

- 正例：使用者問「sync_config.py 怎麼組合檔案」→ 派 Explore 回報結論＋行號，主對話不開檔。
- 反例：主對話自己 `Read` 整支 700 行的 sync_config.py 再回答 → context 燒掉、後續失焦。

## 2. 任務交辦三要素（缺一不派）

每次派工的 prompt 必含（填空範本見 `playbooks/delegation-templates.md`）：
1. **目標與動機**：要什麼＋為什麼要（動機讓 subagent 遇到意外時能做對的取捨）。
2. **驗收條件**：可勾選的完成判準，逐條列。「做好做滿」不是驗收條件，「X 檔案存在且含 Y 段落」才是。
3. **回報格式**：明定回什麼、多長、什麼格式（見下一節回報合約）。

## 3. 回報合約（subagent 端遵守，指揮官端在 prompt 裡引用）

- 只回**結論與判斷**，每個事實附 `檔案:行號`。
- **禁止**貼大段原文；需要保留的長產物**存檔後回傳路徑**。
- 回報長度上限預設 120 行（交辦時可另訂）。
- 失敗就說失敗＋卡在哪＋已試什麼，不硬掰結果。
- 回報開頭第一行＝一句話結論（成／敗／部分完成）。

## 4. 顯式指定 model（預設調度表，2026-07-25 改：opus 優先）

派工時**一律顯式帶 `model` 參數**，不吃預設：

| 任務型態 | model | 理由 |
|---|---|---|
| 一般任務（實作、研究、審查、搜尋、重構——預設起點） | `opus` | 使用者裁定：優先高品質，不再以成本為第一考量 |
| 大量機械重複操作（跑 N 次同型格式檢查、無判斷成分的批次改寫） | `haiku` 或 `sonnet` | 純機械重複、opus 明顯過剩才降級，屬例外非常態 |
| 任務明確綁定 Fable 5（該次特殊 session／使用者指名） | `fable` | 唯一會不派 opus 的情境；日常不主動指定 |

猶豫時：**預設 opus**，除非任務明顯是大量機械重複才考慮降級試水（不確定就仍用 opus）。

## 5. 失敗處理（opus 為預設起點，無更高階可升）

**定義：一輪＝一次模型執行。**

- **opus 失敗** → 若非額度問題，整理失敗軌跡（做法＋錯誤輸出＋驗收差距）回報使用者，換角度重派或請示，不盲目重試同做法。
- **因額度失敗** → 降 `sonnet` 續跑並記 journal，額度恢復後不必補跑；不代表預設政策改變。
- **例外降級的機械批次任務（haiku/sonnet）錯一次** → 直接升 `opus` 重派並附完整失敗軌跡，不留在原級重試。
- **高階解出模式後** → 把解法寫成明確步驟，可**降回便宜模型批次套用**到其餘同型機械案例（僅限機械複製，不適用於仍含判斷成分的任務）。

## 6. 驗證不自驗

**做的人不驗自己**。驗證一律派 **fresh-context** subagent（新開、不給寫作過程，只給產物路徑＋驗收條件）：

| 產物 | 驗法 | 派誰 |
|---|---|---|
| 檔案／文件 | read-back：存在？完整？逐條對驗收條件？（機械核對，維持便宜模型） | `haiku` |
| 程式碼 | 跑測試或實跑，貼實際輸出（不是「看起來對」） | `opus` |
| 高風險判斷 | 第二意見：換模型（或走 ody 換 AI）獨立再判一次；或多答案評審擇優 | `opus` |

驗證 agent 的 prompt 要求它**找碴**（「列出不符合驗收條件之處」），不是「確認沒問題」——後者會順著點頭。

## 7. 本檔的維護

型號表（第 0 節）每次發現不符就即時更新並註記查證日期。其餘規則改動走 `playbooks/maintenance-protocol.md`。
