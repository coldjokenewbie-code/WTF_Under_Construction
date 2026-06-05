# 工作紀錄 2026-06-04 — WTF 主控控制面 + routine realign

> 承接階段二（repo 移出 Drive 已完成）。本 session 把 WTF 從「設定/skills SSOT」推進為「主控所有專案」的控制平面，並修正夜間 routine。

## 1. 完成項目（皆已 commit＋push main）

### SSOT 可達性修復
- **`ddb6631` wtf-root 絕對路徑錨點**：非 WTF 專案（cwd 在 Drive）用相對 `wtf-config/` 抓不到 SSOT → hook/sync 寫 `~/.claude|.codex|.gemini/wtf-root.txt`＝WTF repo 絕對路徑；CLAUDE_CODE/CODEX/GEMINI.md + session-start 改先讀錨點再絕對路徑讀 SSOT。cowork_CDIC 模擬驗證 OK。

### 跨工具與協作
- **`1937fac`**：`deploy_other_tools()` 把 12→10 skills 實體部署到 codex/gemini（保留 find-skills、不 prune）；GLOBAL 加「常駐 monitor 只在 ai-team+明示跨機討論才開」。
- **`286b98e`**：session-start 身分宣告（`{AI}@{host}({OS})`）；GLOBAL 記錄署名慣例 `[AI@機器]`；INDEX 讀取指引。

### 技能精簡
- **`aeb1771`** 12→10：tasklog-naming 併回 GLOBAL.md、刪 cowork-start；清四處引用；deploy_other_tools 加保守 prune。

### 主控控制面（治理/可視，Phase A）
- **`14d8997`**：`sync_config.py` 加 `status`（文字彙整）＋`dashboard`（產 `outputs/dashboard.html`）子指令，掃 registry 各專案 現況(INDEX)＋git＋最新 TaskLog/待辦。
- **`ba77104`**：整合舊 dashboard 的 Fire Evening 設計＋stats row＋即時資料；`_md_inline` 渲染 todo 的 markdown（修「未渲染難讀」）；Edge headless 截圖驗收。

### 夜間 routine realign（依用戶更正）
- **`15fd7f4`**：評估發現 routine 三問題——commit 死分支(自動更新沒生效)、雲端看不到本機 transcript、sync hook 壞一個月、維護舊 dashboard/8-repo。
  - 重寫 `nightly-prompt.md`：**全域設定只「建議」不自改**（lesson 加性可自動）；commit 進 main 只 `git add` 加性檔＋pull-rebase 衝突即 abort；repo 清單→5 個現役；移 broken hook；不碰 dashboard。
  - **通知機制**：routine 寫建議到 `_context/nightly-notify.md`→commit main→本機 pull→**session-start 浮出待核准**（靠 wtf-root 錨點）。
  - 刪舊 root `dashboard.html`、刪 54 個 nightly 死分支。

## 2. 策略決定（存記憶 wtf-control-plane-roadmap）
- WTF→主控所有專案，兩階段：**Phase A 治理/可視（已落地：status/dashboard）**；**Phase B 半自動擷取（語音→Drive _inbox→分流→入專案，待用戶設手機端）**。
- 關鍵：inbox 放 Drive 不放 repo（避免 Drive+git 衝突）；Keep 讀不到（非檔案）；Android 建議 MacroDroid+Autosync。

## 3. 未解決／待用戶
- **必做**：把新 `wtf-config/nightly-prompt.md` 貼回 claude.ai/code 排程 trigger 才生效。
- 4 個非 nightly 殘留分支（add-chat-learning/merge-branches/recover-archived-chat/taiwan-exhibition-halls-table）待用戶確認刪。
- Phase B 擷取端：待用戶設手機 MacroDroid+Autosync 後建 `/inbox` skill。
- 手機推播全域建議（選配 ntfy.sh/Telegram）。
- 儀表板手機看：未定（Obsidian MD vs GitHub Pages）。

## 4. 跨機/跨工具註記
- Mac 已 pull 並修了 `deploy_other_tools` dangling symlink（`8acf046`）。
- 本機 Antigravity(Gemini) agent 另增 GEMINI.md 身分宣告/check 步驟（本 commit 一併保存）。
