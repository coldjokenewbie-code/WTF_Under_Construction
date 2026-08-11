# 問題簡報：Claude 開場不讀/不遵守全域設定 — 實證與待檢草案

> 撰寫：Claude（本案受檢方）[Claude@Mac] 2026-07-15
> 用途：Codex（Tech Lead）解方設計＋agy（質疑者）事實核驗的共同輸入
> 核驗原則：以下每條實證都附可重跑的驗證命令，agy 應實際執行核對，不信文字

## 1. 事件（本 session 實際發生）

1. 使用者要求「啟動studio預覽」，Claude 在 `/Users/coma/git_mirror/claude_CDIC_O4`（版控鏡像）啟動 Remotion Studio，並在後續回答「最新版在哪個資料夾」時宣稱「實際要改檔案、跑指令，用 git_mirror 那份；Drive 這份是唯讀鏡像用途」。
2. 此答案與 SSOT 相反。`wtf-config/GLOBAL.md` 第 42-51 行「Claude_cowork 專案版控鐵律」明文：**Drive 為唯一真相源；git_mirror 僅為版控出口**。
   - 驗證：`sed -n '42,51p' /Users/coma/git_mirror/WTF_Under_Construction/wtf-config/GLOBAL.md`
3. 使用者糾正後追問，Claude 承認：該 session 從頭到尾未完整讀過 GLOBAL.md，直到使用者第三次質疑才執行完整 Read。

## 2. 根因鏈（各環節皆有實證）

### 2a. SessionStart hook 有跑、內容有產出
- Hook 註冊：`~/.claude/settings.json` hooks.SessionStart → `bash ~/.claude/wtf-session-context.sh`
- Hook 正本：`wtf-config/hooks/wtf-session-context.sh`（65 行內）。設計：`CAP=150` 行/檔，把 GLOBAL.md、AGENTS.md、INDEX.md、lessons-learned.md、當前 TaskLog 全文 `head -n 150` 塞進 stdout。GLOBAL.md 132 行、AGENTS.md 90 行，皆未觸發它自己的 150 行截斷。
- 驗證：`cat /Users/coma/git_mirror/WTF_Under_Construction/wtf-config/hooks/wtf-session-context.sh`

### 2b. Claude Code harness 對 hook stdout 有顯示上限（本次的直接斷點）
- 本 session 的 hook stdout 被 harness 持久化成檔案，只有**前 2048 bytes** 以「Preview (first 2KB)」形式直接進入 context；其餘只給檔案路徑。
- harness 訊息原文含：「Output too large (16.9KB). Full output saved to: <路徑>」＋「Preview (first 2KB)」。16.9K 為字元數；持久化檔案實測 **30,968 bytes**（UTF-8，CJK 每字 3 bytes，兩數相容）。
- 「Claude_cowork 專案版控鐵律」標題位於該檔 **byte offset 3613**——在 2KB 預覽之外。**該段規則從未進入本 session context**。
- 驗證：
  ```
  F=$(ls /Users/coma/.claude/projects/-Users-coma-Library-CloudStorage-GoogleDrive-coldjokenewbie-gmail-com------tachart-ihuy-Claude-cowork-projects-claude-CDIC-O4/*/tool-results/hook-4c07eb18-*-stdout.txt)
  wc -c "$F"                                  # 30968
  grep -b "Claude_cowork 專案版控鐵律" "$F"    # 3613:...
  ```

### 2c. Claude 的行為缺陷（不可全歸咎 harness）
- hook 輸出首行寫「已由 SessionStart hook 自動載入，無需再讀這些檔」；harness 同時明示「Output too large／Preview (first 2KB)」。兩訊息矛盾，Claude 採信前者，未讀持久化全文。
- 之後 Claude 對該檔只做過窄關鍵字 grep（`register|hostname|CHECK|OK|STALE|BROKEN|MISSING`，為回報開場身分/檢查狀態而挑），結構上不可能撈到版控鐵律段。
- Claude 自己的開場協議（`~/.claude/CLAUDE.md` 強制初始化協議第 1 步）寫明「讀取全域原則：讀 GLOBAL.md」，Claude 以 hook banner 為由跳過此步。

### 2d. 設計史：此問題是第三次換皮，非首發
- 2026-07-05 前：提醒式 hook（`echo '請讀三檔'`）。廢棄原因（`_context/lessons-learned.md` 2026-07-05 段）：「model 看到後仍需『自覺去讀』，本質靠自律」。
- 2026-07-05：改注入式，宣稱「直接把內容送進 context，model 無需執行任何指令，也無法繞過」。
- 2026-07-09（lessons 同檔）：發現 JSON additionalContext 有 10,000 字元上限（當時內容 63,779 字元已超），改 plain stdout。
- 2026-07-15（本次）：證實 plain stdout 也有 harness 顯示上限（inline 僅 2KB 預覽）。**「注入=保證送達」假設在內容超過某門檻時不成立，且該門檻由 harness 決定、隨版本可變，內容成長必然再撞。**
- 驗證：`grep -n -A5 "2026-07-05\|2026-07-09" /Users/coma/git_mirror/WTF_Under_Construction/_context/lessons-learned.md`

### 2e. 機制真相：現行體系對「讀全域設定」零強制
- Claude Code hook 類型中，SessionStart／UserPromptSubmit 只能注入文字，**不能**擋工具、不能擋回合結束；能機器攔截的是 PreToolUse（可 deny 工具呼叫）與 Stop（可擋回合結束）。
- 本體系已在別處用機器攔截（ody stop_hook.py 掛 Stop、實戰攔截驗證✅；ODY_SQUAD.md 明言「規範停在 prompt 層＝靠 AI 自律必漂移，解＝結構強制」），但「讀 GLOBAL.md」這件事只有 SessionStart 軟注入，無任何 PreToolUse/Stop 守門。
- ODY_SQUAD.md 第 52 行「下一步」早已列「PreToolUse 契約閘（無契約擋 Write/Edit，opt-in）」——方向已知，未落地。

## 3. 使用者的核心質疑（解方必須正面回答）

1. 「你必須立即讀 X.md」與「資料還沒到，去讀」同樣只是文字——**什麼機制強制模型遵守？** 若答案是「沒有」，方案不得再包裝軟提醒為解方。
2. 若存在可強制模型做某事的機制，**為何全域設定本身不是用該機制交付？**
3. 使用者觀察 codex/agy 較守開場規則、Claude 常跳過（此點未驗證，勿當事實引用；但 codex 預設唯讀沙箱=機械強制的例子支持「機制優於措辭」）。

## 4. Claude 草案（受檢對象，Codex 可採可棄）

- **草案 A（已自我撤回，列出供批判）**：hook 在截斷安全區（輸出最前段）印強制指令「若見截斷提示必須先 Read 全文」。撤回原因：仍是文字，與被淘汰的提醒式無機制差異。
- **草案 B**：新增 PreToolUse hook——攔截高風險工具呼叫（至少 Bash/Write/Edit），檢查本 session 是否已有對 GLOBAL.md 的完整 Read 證據（查 transcript 或由 hook 自行維護的 session 標記檔），無則 deny 並回訊「先完整讀 GLOBAL.md」。讀過即放行，之後零成本。
  - 已知待解問題：(1) PreToolUse hook 如何可靠得知「本 session 已讀過」——transcript 路徑/格式依賴 harness 實作；(2) deny 訊息本身也是文字，但差異在「不照做就無法使用工具」，是硬擋；(3) 首次 Read 之前，連「讀 GLOBAL.md 的 Read 呼叫」自己也會過 PreToolUse，須白名單放行 Read 該路徑；(4) Windows/Git Bash 相容。
- **開放問題（Codex 應裁決）**：
  - 強制點選在 PreToolUse（擋工具）還是 Stop（擋收尾）？或組合？
  - 「已讀」的判定資料源：transcript 檔？hook 側 session 狀態檔（如 `/tmp/wtf-read-ack-<session_id>`）？PostToolUse 記錄 Read 事件？
  - 內容送達與遵守是兩件事：送達可解（強制 Read），遵守（讀了照做）是否有任何可機檢代理指標？還是只能靠事後 check（如 ody 閘2）兜底？
  - token 成本：每 session 強制全文 Read（30KB）vs 現行注入，成本相當；是否值得做分段/摘要+隨需全文？

## 5. 解方硬性約束

1. 核心機制必須是機器強制（hook 攔截/exit code/deny），文字提醒只能當輔助 UX，不得當保證。
2. 跨平台：Mac（zsh/bash）＋ Windows（Git Bash）。
3. 不依賴 harness 未文件化的內部行為時最佳；若依賴（如 transcript 格式），須附「行為變更時的失效偵測」。
4. 對每個新 session 的額外 token/延遲成本要量化。
5. 改動落點涉及 `~/.claude/settings.json`（黃區保護路徑）——本輪只提案，部署另需 PO 明授。
