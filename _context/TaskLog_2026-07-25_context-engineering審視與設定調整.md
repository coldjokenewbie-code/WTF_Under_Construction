# TaskLog 2026-07-25：Context Engineering 文章審視與設定調整

> 依據 Claude 官方文章「The new rules of context engineering for Claude 5 generation models」對照本專案設定，並依使用者裁定調整三處規則。

## 1. 本次完成項目

- 完成 Claude 官方文章與現行制度的第一輪對照。
- 依使用者裁定落地 Opus 優先、匯報格式範圍、使用者代號三項修改。
- 完成 Codex 官方手冊補充對照，產出 Claude 修改用交接報告。

## 2. 未解決問題

- **P0**：`GLOBAL.md` 的「便宜 subagent」與 Claude Opus 優先政策矛盾。
- **P0**：`CODEX.md` 綁定不穩定的 `view_file` 工具名稱。
- **P0**：`._agents/skills/` 與 Codex 官方 `.agents/skills/` 不一致；尚未查證 Claude 原生路徑與安全遷移方式。
- **P1**：Codex 重複載入 `AGENTS.md`，且共用規則帶入 `.claude/CLAUDE.md`。
- **P1**：既有 HTML 報告把官方六項轉變寫成五項。

## 3. 主要輸入檔案

- `wtf-config/GLOBAL.md`
- `wtf-config/AGENTS.md`
- `wtf-config/CODEX.md`
- `wtf-config/playbooks/model-dispatch.md`
- `outputs/context-engineering-review_20260725.html`

## 4. 下一步建議

- Claude 依 `_context/Handover_2026-07-25_context-engineering跨模型規範優化.md` 的 P0→P1 順序修改並驗收。

## 文章對照評估摘要

四個轉變：規則→判斷力／範例→介面設計／預載→漸進揭示／重複指令→工具描述。

- **規則→判斷力**：AGENTS.md 溝通原則多數屬主觀品味（語氣、繁中用語、禁詞），非模型可推斷的通用行為，不受此轉變影響，不宜比照文章邏輯裁減。
- **範例→介面設計**：`playbooks/delegation-templates.md` T1-T5 填空範本是典型待改對象；已在對話中示範 T1（schema 化）／T5（改用 `ReportFindings` 工具，格式規範交給參數而非文字）的改寫方向，未落地成正式修改（使用者表示 Q2 的延伸探討不適合在本專案問，暫緩）。
- **預載→漸進揭示**：本專案的 playbooks 路由表＋skills lazy-load 架構本身已符合此原則，走在文章建議前面。落差在於 GLOBAL.md／AGENTS.md 兩檔（合計 9148 字元）被 `wtf-session-gate` 設計為每 session 強制全讀——這是刻意的基礎設施可靠性設計（見下方「wtf-session-gate 判斷」），非文章要打擊的「行為性規則預載」，兩者性質不同。
- **重複指令→工具描述**：delegation-templates 每個範本結尾重貼「回報要求」，若改用 Workflow 的 `agent(prompt,{schema})`，這段可省，交給參數 required/description 承擔。

## 使用者裁定並已落地的三項調整

### 1. 模型調度政策：opus 優先（黃區，使用者直接指示＝已核准）
`wtf-config/playbooks/model-dispatch.md` 第 0／4／5／6 節改寫：預設派工一律 `opus`，不再以成本優化為主；例外僅「任務明確綁定 Fable 5」與「大量機械重複操作」兩類。舊「haiku→sonnet→opus 逐級升級」的成本優化邏輯全面讓位。額度緊縮備援（opus 因額度失敗才降 sonnet）保留但降為次要備援，不影響預設政策。

### 2. 輸出格式規則範圍限縮（黃區，使用者直接指示＝已核准）
`wtf-config/GLOBAL.md`「輸出格式」條：原「文件輸出一律 HTML，不用 Word」誤把「agent 向使用者匯報」與「業主端正式交付物」兩種情境混為一談。改為：僅「agent 向使用者（PO）本人匯報」優先用 HTML；業主／廠商端交付物依各專案慣例（docx/pptx 等）不受此限。

### 3. 使用者代號＝三藏（黃區，使用者直接指示＝已核准）
`wtf-config/AGENTS.md`：角色定義表 Product Owner 列加註「代號：三藏」；用語規範表下方加說明——寓意與一群 agent 在未知任務旅途中合作解決難題（仿《西遊記》師徒取經）。用於角色定義／跨 agent 記錄等正式指涉場合，一般對話仍用「你」／「使用者」，不強制每句代入。

## wtf-session-gate 判斷（使用者交付判斷權，非直接指示）

使用者對前次回覆中「預載→漸進揭示」段落表示看不懂，猜測是「先前制定的提升較低等級模型能力的規範」——**猜對了**：`wtf-session-gate` 建於 2026-07-09 前後，動機是實測發現「規則寫進 context ≠ 模型真的完整讀過或照做」（尤其舊世代模型），需要結構性的收據機制去確認。

**現況**：2026-07-22 已修好其中兩個 bug（bundle SHA 過期、postread 缺檔崩潰），但 `PreToolUse`／`Stop` 兩個「真正會擋下操作」的 hook 從未在 `settings.json` 註冊——這套閘目前**只被動記錄「讀完了沒」，不會阻擋任何操作**。

**判斷（維持現況，不做進一步變動）**：
1. 三天前才修好，功能正常，沒有新增的具體故障或阻力可以指出需要再改。
2. 拆除等於放棄「未來如真的需要嚴格擋」的備援能力；保留成本很低（安靜記錄，不影響任何操作），拆除沒有對應的實質效益。
3. 文章講的「信任模型判斷力」針對的是**行為性規則**（系統提示詞裡教模型怎麼做決策），跟這裡要解決的**基礎設施可靠性問題**（確定關鍵設定檔真的被載入、且過程未被覆蓋）是兩件不同的事——本專案過去有實測案例（07-09 lessons）證明「模型讀到 context 內容≠會照做／完整讀完」，這是既有選擇用機器擋取代自律的具體理由，跟模型世代無關。
4. 若之後此機制再出新 bug 或造成明顯干擾，屆時重新評估是否整套拆除；本次不主動變更。

## 待辦
- Windows 端 `~/.claude/settings.json` 若也寫死 `WTF_BUNDLE_SHA256`（見 07-21 TaskLog），仍待下次 Windows session 處理，與本次調整無關，不重複列。
- delegation-templates.md T1-T5 schema 化重寫：使用者表示現階段不在本專案深入，暫緩，待使用者主動提起再做。

## Codex 補充審視（2026-07-25）

Codex 依 Anthropic 原文與 OpenAI Codex 官方手冊重新對照後，發現現行制度另有四項跨工具落差，交由 Claude 修正；完整範圍與驗收條件見：

- `_context/Handover_2026-07-25_context-engineering跨模型規範優化.md`

補充結論：

1. 共用 SSOT 應保存專案事實、不可逆限制與驗收標準；模型、權限、工具名稱與原生載入方式應放各工具轉接層。
2. `GLOBAL.md` 的「便宜 subagent」與 Claude 最新「Opus 優先」政策矛盾；共用規則不應指定成本或模型。
3. `CODEX.md` 指定 Codex 不一定存在的 `view_file`，且要求重讀原生已載入的專案 `AGENTS.md`，應改為工具中立描述並移除重複載入。
4. `._agents/skills/` 不是 Codex 官方原生掃描路徑；Codex 官方路徑為 `.agents/skills/`。遷移前須同時確認 Claude 的部署方式，禁止直接改名造成另一工具失效。
5. Anthropic 原文列出六項轉變；既有 HTML 報告寫成五項，且把「豐富參考資料」縮寫為「References as code」，需更正。
6. Auto-memory 是補充層，不取代跨工具 SSOT 中明確、穩定的使用者偏好。

## Claude 執行結果（2026-07-25，依 Handover P0→P1 順序）

同一天另有使用者依三份獨立 HTML 報告（本檔 outputs 版＋ Assembly_Plant_Mobile_Guide／cowork_CDIC 兩份 Claude 報告）核准的 5 項行動，與本節 Codex Handover 的 P0/P1 有重疊，一併處理：

- [x] **P0-1**（＝使用者核准 5 項之第 2、3 項的底層問題）：`GLOBAL.md`「派工鐵律」改寫為風險／獨立性判斷，移除「便宜 subagent」「顯式指定 model」等 Claude 專屬用語，改工具中立描述；Claude 專屬模型調度仍全部留在 `model-dispatch.md`（已依使用者兩輪裁定改為「派適合的 agent」，非固定 opus）。
- [x] **P0-2**：`CODEX.md` 移除 `view_file` 具名工具，改「讀取指定檔案」；同時依 P1-1 移除重複讀取 `wtf-config/AGENTS.md` 的步驟（已查證：每個已註冊專案根目錄的 `AGENTS.md` 是 sync 部署的同步副本，Codex 原生會照專案目錄層級載入，不必再手動重讀一次）。
- [x] **P0-3 查證完成，未執行遷移**：委託 claude-code-guide 查證 Claude Code 專案 skill 原生路徑＝`.claude/skills/`（官方文件 code.claude.com/docs/en/skills.md 實查）；Codex 官方路徑為 `.agents/skills/`——**兩者不同，非單一共用資料夾能解決**。現況 `._agents/skills/` 兩邊都不是原生路徑，純靠 AGENTS.md 指示模型手動查看，不是任一工具的原生自動發現。真正修法需 `sync_config.py` 新增邏輯，把每專案 `._agents/skills/` 內容分別複製到該專案的 `.claude/skills/`（給 Claude）與 `.agents/skills/`（給 Codex）兩份，SSOT 仍留中立目錄。**此項屬 `sync_config.py` 黃區變更，效益與工程量需使用者拍板，本次未執行**，僅完成查證與方案。
- [x] **P1-2**：`AGENTS.md` 溝通原則依 Codex 給定的精確保留/合併清單去重（保留：繁中台灣用語、禁您、使用者/業主/廠商定義、未驗證標註、執行成功才回報、禁虛構+連結驗證；合併：效益優先/精簡定義/文風基準/禁浮誇 五條→一條判準＋具體示範），未按「文章刪 80%」的比例硬砍，符合 Codex「去重不是砍比例」的提醒。
- [x] **P1-3**：與 P0-1 一併完成（GLOBAL.md 數字門檻→風險/獨立性判斷）。
- [x] **P1-4**：`outputs/context-engineering-review_20260725.html` 修正為官方六項轉變（原五項漏列「重複指令→工具描述」「CLAUDE.md 記憶→Auto-memory」兩條並與「CLAUDE.md 輕量化」混寫）；「References as code」改列為「豐富參考資料」的子類；新增「D. Codex 跨工具差異」段落。
- [x] 使用者核准的原 5 項行動：`delegation-templates.md` 全面介面化改寫（含新增 T-視覺類範本、Workflow schema 替代方案）；cowork_CDIC `rules/translation-bilingual-docx.md`（146→9 行指標）＋新 skill `._agents/skills/translate-bilingual-docx/SKILL.md`（151 行，內容無遺漏，經 fresh-context read-back 確認）；Assembly_Plant_Mobile_Guide 新 `rules/exhibit-content-template.md`（33 行，欄位對照 `types.ts:35-47` `Exhibit` 型別逐一核實，無自行發明欄位）。
- [x] `sync_config.py check`：全數 OK，19 個專案 AGENTS.md 與 `~/.claude/` 皆與真相源一致，bundle SHA 已隨最新內容換代（`d5c5d33ca0f9…`）。

### 未完成／待使用者裁決

- **P0-3 的實際遷移**（sync_config.py 新增雙路徑複製邏輯）：方案已備，工程量與跨工具影響需使用者拍板是否執行。
- **「fresh-context 驗證 Codex 實際載入」**：無法在本 Claude Code session 內驗證 Codex 的實際載入結果（`codex debug prompt-input` 需在 Codex CLI 內執行），此項留待下次有 Codex session 時驗證，不可視為已完成。
- cowork_CDIC 新 skill 的邊界內容（glossary 讀法在指標檔與 skill 內有輕微重複）：執行 agent 已列出，判斷為可接受的必要重複，未進一步精簡。
