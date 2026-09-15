# Handover 2026-09-14｜ai-team：跨工具 skill 取用對等 × 模型調度表更新 × GLOBAL.md 瘦身

> 前手：[Claude@comaMacBookAir]（Opus 5, 1M context），擔任 ai-team Tech Lead，第 2 輪討論前中止。
> 接手：Codex（PO 指定）。接手後你就是 Tech Lead。
> PO＝三藏。本檔為交接真相源；討論脈絡與已驗證事實全在此，不必重跑驗證。

---

## 1. PO 的原始指令（逐條，不得漏）

1. `/ai-team`，**Claude 為 lead**（現移交 Codex）。
2. 「請妥善使用你的額度」＝成本意識寫進設計判準，不是口號。
3. 「跟 Claude Fable 5.1 討論，**agy 先不用**」——本輪不呼叫 Antigravity。
4. 「目前你似乎無法取用 claude 的 skill／照理說我的規劃是**所有 AI 都要可以取用**」。
5. 「檢閱一下 WTF 的架構，針對**你跟 Fable 5.1 的能力**，提出優化方案」。

## 2. 已驗證事實（本機實測，有證據，接手者不必重驗）

| # | 命題 | 結果 | 證據 |
|---|---|---|---|
| V1 | Fable 5.1 headless 能否取用 skill | **能**。17 個 WTF skill 全列出 | `claude -p --model claude-fable-5-1 "…列出可用 skill"` |
| V2 | Codex 有無原生 Skill 工具 | **無**（自稱屬實） | `codex exec "…你有沒有可用的 Skill 工具"` → 「無 Skill 工具」 |
| V3 | Codex 實際上載不載得到 skill | **載得到**。未提「skill」二字即自行讀取 `~/.codex/skills/session-start/SKILL.md`、`~/.codex/skills/handover/SKILL.md` | `codex exec "請幫我為目前這個工作階段產出交接文件…"` 行為測試 |
| V4 | Agent tool 的 model 參數 | enum＝`["sonnet","opus","haiku","fable"]`，**fable 可派** | Opus 5 session 的 Agent tool schema |
| V5 | 型號 ID（權威值） | Fable 5.1＝`claude-fable-5-1`／Opus 5＝`claude-opus-5`／Sonnet 5＝`claude-sonnet-5`／Haiku 4.5＝`claude-haiku-4-5-20251001` | Opus 5 session 系統層給定 |
| V6 | 設定同步狀態 | `sync_config.py check` 全 OK（25 項） | 本機執行 |
| V7 | nightly-notify | 無未勾 `- [ ]` 建議 | 讀檔 |

**V2/V3 是本次最重要的修正**：PO 的疑慮「所有 AI 都能取用 skill」在 Codex 端**結果上已達成，但機制不同**——Claude 系走原生 Skill 工具，Codex 走 `~/.codex/AGENTS.md` 文字協議＋shell 讀檔。
前手原本誤判「`~/.codex/skills/` 是死檔」，被 Fable 5.1 要求做行為驗證後推翻。**不得採信模型自稱，要用行為測試。**

**剩餘風險（待你評估與收口）**：
- (a) Codex 的成功是**模型自律＋glob 資料夾名稱猜測**，沒有索引、沒有觸發詞表，非確定性行為。
- (b) 換模型／換 CLI 版本可能就不做了（本次實測版本：codex-cli 0.153.4 / gpt-6-astra / reasoning xhigh）。
- (c) **Antigravity 端完全未驗證**（PO 指示本輪不用 agy）——`~/.gemini/skills/` 已有複製，是否真載入未知。

## 3. 架構現況數據（已量測）

- 每 session 無條件注入：`GLOBAL.md` 8,343 字 ＋ `AGENTS.md` 3,320 字 ＋ 工具層檔（`CLAUDE_CODE.md` 1,430／`CODEX.md` 1,372／`GEMINI.md` 1,876）≈ **13,000 字**。
- `playbooks/` 15 檔共 **39,530 字**（按需，GLOBAL.md 內有路由表）。
- `wtf-config/skills/` 17 個 SSOT skill → 實體複製到 `~/.claude/skills/`、`~/.codex/skills/`、`~/.gemini/skills/`。
- **`model-dispatch.md` 第 0 節已過時**：查證日 2026-07-03，表上寫「高階判斷＝Opus 4.8 `claude-opus-4-8`」「Fable 5 已不可得、日常勿指定」。兩條皆與 V4/V5 不符。

## 4. 第 1 輪討論結果（Fable 5.1 已回，全文摘要）

**A（skill 跨工具可攜性）**：正解＝「skill ＝有觸發描述的 playbook」，由 sync 生成一份索引（名稱＋觸發條件＋絕對路徑）寫進各工具指示檔，用原生檔案讀取載入，不需新機制。理由：Claude 的 Skill tool 本質只是「模型判斷觸發→讀一個 markdown 進 context」，與 GLOBAL.md 的 playbook 路由表是同一套系統的兩種觸發方式。
- Loader CLI＝功能等於 `cat`，沒解決「誰決定何時載入」，價值只剩 lint，可被 `sync_config.py check` 吸收。
- **MCP server 化＝假解法**：多一個常駐程序、各工具 MCP 支援度不一，最後回傳的仍是同一段 markdown，用基礎設施換對稱感。
- **現狀也是假解法**：資料夾複製了、指示檔寫「照協議載入」，看起來部署了。（※ 此點已被 V3 部分推翻——Codex 實際讀得到，但非確定性。）

**B（Opus 5 ＋ Fable 5.1 搭檔）**：Fable 的優勢是判斷力與獨立性，該派的是「錯了代價高、且必須 fresh context」的任務；讀取密集的扇出仍派 Sonnet／Haiku。
- Agent tool 派 fable → 跨檔診斷、架構取捨、需要主 session 脈絡的第二意見。
- `claude -p` 派 fable → **獨立驗收**（ai-team「不自驗自過」正需要無狀態、不受 Tech Lead 假設污染的驗證者）、排程／跨程序任務。代價：每次重付 13k 字注入，交辦必須自足。
- 不該派 Fable：搜尋摘要、機械改檔、需反覆來回的小修。
- **判準**：「這件事若 Sonnet 答錯，你發現得了嗎？發現不了才派 Fable。」

**C（context 稅）**：13k 字在 1M 窗口佔比不到 2%，窗口大小不是問題；問題是**規則條數越多、單條遵從率越低**（呼應 `harness-diagnosis.md` 的「說完成但沒完成」），且每個 subagent／每次 `claude -p` 都重付。判準：
- **必須常駐**：影響每一句輸出的規則（溝通原則）；觸發詞出現前模型不會自知需要的規則（版控：看到「git」即查）——但只留「觸發詞＋一行結論＋指標」。
- **可降級**：有明確情境、且情境可從一行指標辨識的全文（存檔路徑細則、數據引用細則、Excel 字體、預覽命令參數）。
- **漂移根因**：每次 PO 裁定就把全文塞進 GLOBAL.md。修法＝在 `maintenance-protocol.md` 立規：裁定＝一行入 GLOBAL、細則入 playbook。

**D（優先序）**：**型號表 → A → C → B**。型號表十分鐘可修卻讓每次派工建立在錯誤資訊上，還壓抑了 Fable 的日常使用；A 次之，PO 相信 Codex 有 skill 而機制其實不確定，交辦品質會**靜默衰減**，是目前最大隱性損失；C 損失最慢但最持久，應以維護規則收口而非一次性瘦身。

## 5. 下一步：第 2 輪討論（prompt 已寫好，未送出）

第 2 輪的完整 prompt 存於本檔附錄 A。要 Fable 給的是**可直接落地的設計**，四項：
1. skill 索引的具體規格（欄位、範例列、觸發詞寫法、放哪、Claude 系會不會重複觸發、17 列內聯是否反加重 context 稅）。
2. `model-dispatch.md` 第 0 節型號表與第 4 節派工對照表的**完整改寫內容**（含 Opus 5／Fable 5.1 兩列，區分 Agent tool 派 fable 與 `claude -p` 派 fable，成本判準入表）。
3. GLOBAL.md 瘦身的**逐節刀法**（常駐全文／降級一行指標＋playbook／刪除，每項標明用 C 段哪條判準）。
4. 執行順序與驗收方式（Tech Lead 自做哪些、派出哪些、驗收者要看什麼證據才 PASS）。

## 6. 接手後的協議約束（ai-team skill，不得跳步）

- 動工前**至少討論 3 輪**（目前完成 1 輪，第 2 輪 prompt 已備）。無共識不得動工。
- 執行後**輪流驗收**，**禁止自驗自過**；Tech Lead 自己執行的也要交小隊驗。
- 全部驗收通過後**交 PO 驗收，不可自行 commit**。
- 呼叫 Claude／Fable：`claude -p --model claude-fable-5-1 "<prompt>"`（Mac 無 `timeout` 指令，別用；要限時改 `gtimeout`）。
- 本輪**不呼叫 agy**（PO 指示）。
- WTF_Under_Construction 是版控鐵律的**唯一例外**：本體直接在 `git_mirror/`，不走 Drive 鏡像。

## 7. 待 PO 拍板 / 附帶發現

1. **Antigravity skill 取用是否要一併驗證**（本輪 PO 說先不用 agy，但「所有 AI 都能取用」的目標缺這一塊就不完整）。
2. **`.claude/settings.local.json` 權限規則警告**（本 session 實際跳出）：
   `Bash(grep -o "E:\\\\Git_work[^\"]*" ~/.claude/settings.json)` 的萬用字元位置在命令其餘部分之前，會連帶批准插入的任意選項。建議把 `*` 換成確切值，或只在 subcommand 之後使用 `*`。另注意該規則內容指向已禁用的 `Git_work` 路徑。
3. 前手未做任何檔案修改，工作區乾淨；本檔為唯一新增檔（尚未登錄 INDEX.md，接手後請補一行指標）。

---

## 附錄 A：第 2 輪 prompt 全文（直接複製給 Fable 5.1）

```
ai-team 第 2 輪。你是 Fable 5.1，Tech Lead 是 Codex。繁體中文台灣用語，只輸出文字不讀寫檔。

## 你第 1 輪的結論（Tech Lead 已收下，摘要）
A：skill＝有觸發描述的 playbook，sync 生成索引（名稱＋觸發條件＋絕對路徑）寫進各工具指示檔；MCP server 化與現狀資料夾複製都是假解法。你要求用行為驗證，不採信模型自稱。
B：Agent tool 的 model 參數含 fable，所以共享 context 的 Fable 可得；claude -p 的價值在獨立無狀態驗收。判準＝「Sonnet 答錯你發現得了嗎？發現不了才派 Fable」。
C：1M 窗口下 13k 字佔比不是問題，問題是規則條數多→單條遵從率降；砍「事後被內聯的鐵律全文」，並在 maintenance-protocol 立規收口。
D：型號表 → A → C → B。

## Tech Lead 依你要求做的兩項驗證（其中一項推翻原本的診斷）

驗證 1：Codex 行為測試（你是對的）
交辦 codex exec「請幫我為目前這個工作階段產出交接文件…」，不提 skill 兩字。Codex 回答「有實際讀到 skill 定義檔」並列出 ~/.codex/skills/session-start/SKILL.md、~/.codex/skills/handover/SKILL.md。
→ 結論修正：Codex 沒有原生 Skill 工具（自稱屬實），但走 ~/.codex/AGENTS.md 的文字協議＋shell 讀檔，實際成功發現並讀取了正確的 SKILL.md。所以 ~/.codex/skills/ 不是死檔，是靠文字協議驅動的。你提的「文字路由表」解法其實已經半成型地在運作。
→ 剩餘風險（請評估嚴重性）：(a) 這是模型自律的偶然成功，沒有索引、沒有觸發詞，Codex 靠 glob 資料夾名稱猜；(b) 換模型／換版本可能就不做了；(c) Antigravity 端完全未驗證。

驗證 2：Agent tool 的 model 參數（你說對了）
model enum 實際值＝["sonnet","opus","haiku","fable"]。派 Fable 有兩條路：Agent tool（共享 context、結構化回傳、同額度池）與 claude -p（獨立無狀態）。

## 權威型號資料（可直接寫進型號表）
Fable 5.1＝claude-fable-5-1／Opus 5＝claude-opus-5／Sonnet 5＝claude-sonnet-5／Haiku 4.5＝claude-haiku-4-5-20251001
Agent tool model 參數值：opus / sonnet / haiku / fable
現行 model-dispatch.md 第 0 節寫「高階判斷＝Opus 4.8 claude-opus-4-8」「Fable 5 已不可得、日常勿指定」——兩條都過時。

## 第 2 輪要你給「可直接落地的設計」，不要再給方向
1. skill 索引的具體規格：sync_config.py 要生成什麼？給出索引檔的實際欄位與一列範例（含觸發詞怎麼寫才能讓非 Claude 系工具可靠命中）。寫進哪裡（各工具指示檔內聯？還是獨立檔＋指示檔一行指標？）？Claude 系有原生 Skill 工具、會不會與索引重複觸發、要不要對 Claude 系隱藏索引？17 個 skill 的索引若內聯，會不會反而加重你 C 段警告的 context 稅——給取捨判準。
2. model-dispatch 第 0 節與第 4 節改寫：直接給出「型號表」與「派工對照表」兩張表的完整 markdown，含 Opus 5 與 Fable 5.1 兩列，並明確區分「Agent tool 派 fable」與「claude -p 派 fable」各自適用情境。成本意識寫進判準（PO 指示：妥善使用額度）。
3. GLOBAL.md 瘦身的具體刀法：現有大節為——開場協議／派工與判斷（含按需路由表）／Claude_cowork 版控鐵律（最長，約佔四分之一）／工作品質底線（含數據引用鐵律、交付即預覽、存檔預設路徑鐵律三大段）／全域設定的維護／檔案命名與輸出規範。逐節判定「常駐全文／降級成一行指標＋playbook／刪除」，說明每個判定用的是 C 段哪一條判準。具體到節名。
4. 這次的執行順序與驗收方式：依 ai-team 協議動工後要輪流驗收、不自驗自過。提出 Tech Lead 該自己做哪幾項、哪幾項派出去、以及你作為驗收者要看什麼證據才算 PASS。

輸出四段 ## 1 ## 2 ## 3 ## 4。表格完整寫出可直接貼用。總長 1400 字內。
```
