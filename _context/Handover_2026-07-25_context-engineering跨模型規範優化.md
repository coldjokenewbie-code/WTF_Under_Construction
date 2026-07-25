# Context Engineering 跨模型規範優化報告暨 Claude 交接

> 日期：2026-07-25  
> 審視者：Codex@comaMacBookAir.local  
> 接手者：Claude  
> 任務性質：修改 WTF 全域／工具層規範；不是全面重寫制度。

## 1. 現況摘要

現行架構已有三項正確方向：

1. `_context/INDEX.md → 當前 TaskLog → lessons-learned.md` 三檔制。
2. playbooks 按情境路由、skills lazy-load。
3. 專案狀態、教訓與驗收證據寫入 repo，不依賴對話記憶。

Claude 先前已依使用者裁定完成三項修改，本次不得回退：

1. Claude 派工預設 Opus 優先；大量機械操作與明確綁定其他模型屬例外。
2. HTML 優先僅限 agent 向使用者匯報；業主／廠商正式交付物依專案慣例。
3. 使用者正式代號為「三藏」，一般對話仍用「你／使用者」。

`wtf-session-gate` 維持目前被動記錄、不阻擋操作的狀態；本次不拆除、不擴大。

核心判斷：不要把 Claude 5 的提示詞直接複製給 Codex。應採「共用 SSOT＋工具轉接層＋當次任務」三層：

| 層級 | 應包含 | 不應包含 |
|---|---|---|
| 共用 SSOT | 專案事實、角色、不可逆限制、驗收標準、跨工具交接格式 | 特定模型名稱、特定工具名稱、某工具的權限參數 |
| 工具轉接層 | Claude／Codex／Gemini 的載入路徑、模型調度、sandbox、hook、權限與工具陷阱 | 跨專案業務事實的重複副本 |
| 當次任務 | 目標、相關來源、限制、輸出、完成條件 | 可由 repo 或工具自行發現的逐步遙控 |

## 2. 檔案位置

### 本次主要依據

- `wtf-config/GLOBAL.md`
- `wtf-config/AGENTS.md`
- `wtf-config/CODEX.md`
- `wtf-config/playbooks/model-dispatch.md`
- `wtf-config/playbooks/delegation-templates.md`
- `_context/TaskLog_2026-07-25_context-engineering審視與設定調整.md`
- `outputs/context-engineering-review_20260725.html`

### 已實開驗證的官方來源

- Anthropic：<https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models>
- OpenAI Codex 最佳實務：<https://learn.chatgpt.com/guides/best-practices>
- OpenAI Codex Skills：<https://learn.chatgpt.com/docs/build-skills>
- OpenAI Codex Subagents：<https://learn.chatgpt.com/docs/agent-configuration/subagents>

## 3. 緊急修復

### P0-1：共用派工規則與 Claude 模型政策矛盾

症狀：

- `GLOBAL.md` 仍寫「派便宜 subagent」與「一律顯式指定 model」。
- `model-dispatch.md` 已依使用者裁定改為 Claude 預設 Opus。
- Codex 的可用模型、reasoning 與 subagent 呼叫介面不同，不能沿用 Claude 的全域要求。

建議修法：

1. `GLOBAL.md` 改為工具中立判準，例如「把可獨立、會產生大量中間輸出的工作交給適合的執行 agent；主對話只收結論與證據」。
2. 從共用規則移除「便宜」與「顯式指定 model」。
3. Claude 的型號與升降級政策只留在 `model-dispatch.md`。
4. Codex 的模型／reasoning 政策放 `CODEX.md` 或 `.codex/config.toml`，不得回寫共用模型名稱。

驗收：

- 全 repo 搜尋「便宜 subagent」不再出現在跨工具共用規則。
- `GLOBAL.md` 不指定 Claude／Codex 型號。
- `model-dispatch.md` 的 Opus 優先裁定仍存在。

### P0-2：Codex 規範綁定不存在或不穩定的工具名稱

症狀：

- `CODEX.md` 指定「以 `view_file` 讀」，但 Codex 工具表不保證存在此名稱。

建議修法：

- 改成「讀取指定檔案」，禁止在規範中指定非穩定工具名稱；只有確定的 Codex 原生設定鍵或 CLI 指令才可具名。

驗收：

- `CODEX.md` 不再出現 `view_file`。
- 開場協議仍能清楚指出必讀來源。

### P0-3：專案 skill 路徑與 Codex 原生路徑不一致

症狀：

- `AGENTS.md` 宣稱工具中立目錄為 `._agents/skills/`。
- Codex 官方文件指出 repo skill 原生掃描路徑為 `.agents/skills/`。
- 本 repo 目前未建立上述任一目錄，現況主要依賴全域 skills 實體副本。

建議修法：

1. 先查證當前 Claude Code 對專案 skills 的原生路徑。
2. 若 Claude 不原生讀 `.agents/skills/`，以 `.agents/skills/` 作工具中立 SSOT，再由 `sync_config.py` 實體複製到 Claude 原生位置；維持禁止 symlink。
3. 若存在既有專案專屬 skill，先列清單與 checksum，再遷移；禁止直接 rename 或刪除。
4. 修正 `AGENTS.md`、`sync_config.py`、部署檢查與相關教學文件中的路徑。

驗收：

- Codex 新 session 可原生列出一個測試專案 skill。
- Claude 新 session 可列出同一 skill。
- 兩邊讀到的 `SKILL.md` 內容一致。
- 無 symlink、無同名重複 skill、無遺失專案客製檔。

## 4. 技術細節與修改原則

### P1-1：縮短 CODEX.md，但保留可靠初始化

目前問題：

- Codex 已原生載入全域與就近的 `AGENTS.md`，`CODEX.md` 又要求手動讀取同一份 `wtf-config/AGENTS.md`。
- 共用 `AGENTS.md` 還要求讀 `.claude/CLAUDE.md`，把 Claude 專屬設定帶入 Codex。

修改方向：

1. `~/.codex/AGENTS.md`／`wtf-config/CODEX.md` 只保留：
   - SSOT 錨點。
   - 新 session 呼叫 `session-start`。
   - Codex 專屬 sandbox／approval／固定命令前綴等陷阱。
   - Codex 任務訊號 AgentID。
2. Codex 原生已載入的專案 `AGENTS.md` 不再重讀。
3. `.claude/CLAUDE.md` 只由 Claude 轉接層載入；共用規則不得要求所有工具讀取。
4. 模型、reasoning、sandbox、approval、MCP、hook 等可機械配置者，優先放 `.codex/config.toml`，不要用自然語言重複描述。

### P1-2：AGENTS.md 溝通規則採「去重」，不是「刪 80%」

Anthropic 刪除 80% 系統提示的實驗只證明其 Claude 5 產品情境可縮減，不能直接推論本專案也應刪相同比例。

保留：

- 繁體中文與台灣用語。
- 禁止尊稱「您」。
- 使用者／業主／廠商定義。
- 未驗證內容標註。
- 執行成功後才能回報完成。
- 禁止虛構、連結須實開驗證。

可合併：

- 「效益優先、精簡定義、禁止過渡語、文風基準、禁止浮誇」有語意重複，可濃縮成判準＋少數不可推斷的硬偏好。

不得將穩定偏好只交給 Auto-memory；Auto-memory 是補充層，不能取代跨工具 SSOT。

### P1-3：數字式派工門檻改為風險／獨立性判斷

目前「超過 300 行、超過 3 檔必派」過於僵化。建議改為：

- 適合派工：工作可獨立、讀取密集、中間輸出會污染主 context、可以平行處理。
- 不適合派工：修改彼此高度耦合、多人同時寫同一區域、協調成本高於執行成本。
- 高風險成果：fresh-context 或跨模型獨立驗證。
- 低風險單點修改：允許主 agent 自行執行命令與 read-back，不強制每次另派 agent。

Claude 的具體 model routing 留在 `model-dispatch.md`；Codex 依其原生 subagent、模型與 reasoning 機制另寫短規則。

### P1-4：修正既有 HTML 報告

`outputs/context-engineering-review_20260725.html` 需修正：

1. 官方不是五項，而是六項：
   - 規則 → 判斷
   - 範例 → 介面
   - 全部前置 → 漸進揭露
   - 重複指令 → 簡單工具描述
   - CLAUDE.md 記憶 → Auto-memory
   - 簡單規格 → 豐富參考資料
2. 「References as code」改為「豐富參考資料」；程式、測試、HTML、mockup、rubric 都只是其子類。
3. Auto-memory 不取代跨工具 SSOT。
4. 補入 Codex 的 `AGENTS.md`、`.agents/skills/`、`.codex/config.toml` 與 subagent 差異。

## 5. 後續待辦

### Claude 本次應完成

- [ ] 讀 `wtf-config/playbooks/maintenance-protocol.md`，依權限區執行。
- [ ] 修正 P0-1、P0-2。
- [ ] 查證 Claude 專案 skill 原生路徑後處理 P0-3；證據不足時只提出遷移方案，不直接搬檔。
- [ ] 依 P1-1 縮短 `CODEX.md`，但先用 `codex debug prompt-input` 驗證載入結果。
- [ ] 依 P1-2 去重 `AGENTS.md`；不得按固定比例刪除。
- [ ] 依 P1-3 重寫共用派工判準。
- [ ] 修正 HTML 報告六項轉變與 Codex 差異。
- [ ] 更新本 TaskLog 與 `_context/INDEX.md`。
- [ ] 執行 `sync_config.py check`；有 STALE／BROKEN／MISSING 才執行 `sync`。
- [ ] fresh-context 驗證 Claude 與 Codex 各自實際收到的指令，附命令與摘要。

### 禁止事項

- 不回退三項使用者已裁定修改。
- 不拆 `wtf-session-gate`。
- 不以文章的 80% 當本專案刪減 KPI。
- 不把 Claude 模型名稱寫進跨工具共用規則。
- 不直接刪除／改名 skills 目錄。
- 不覆寫工作區既有未提交變更；先檢查 diff、逐檔處理。

### 完成定義

1. 共用規則不含互相矛盾的模型／成本要求。
2. Claude、Codex 各自只載入必要的工具層設定，沒有手動重讀同一份 `AGENTS.md`。
3. 專案 skill 在 Claude 與 Codex 均能被發現，且真相源唯一。
4. HTML 報告與兩家官方文件一致。
5. `sync_config.py check` 全數通過。
6. Claude 與 Codex fresh session 的實際載入證據已寫入 TaskLog。
