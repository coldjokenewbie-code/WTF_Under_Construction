# Claude Code 工具層設定
> 適用：Claude Code CLI / IDE Extension
> 載入方式：`~/.claude/CLAUDE.md` 指向此檔；本機自動載入

**【強制初始化協議】對話開始時，必須立即執行以下步驟，不得跳過：**
0. **定位 SSOT（絕對路徑）**：讀 `~/.claude/wtf-root.txt` 取得本機 WTF repo 絕對路徑 `<WTF_ROOT>`（此檔由 hook／`sync_config.py` 寫出；`wtf-config` 已移出工作區，**不可用相對路徑**）。讀不到時 fallback：讀專案本地 `AGENTS.md`（sync 已部署），並回報「SSOT 錨點缺失，請先跑一次 hook 或 `sync_config.py sync`」。
1. **讀取全域原則**：以 `view_file` 讀取 `<WTF_ROOT>/wtf-config/GLOBAL.md` 載入全域溝通與效益原則。
2. **讀取 Agent 協議**：以 `view_file` 讀取 `<WTF_ROOT>/wtf-config/AGENTS.md` 載入跨工具 Agent 協作與信號通訊協議。
3. **讀取專案知識**：
   - 讀取 `_context/` 中所有 `.md` 檔案。
   - 讀取 `rules/` 中所有 `.md` 檔案（若存在）。
4. **向用戶說明「已載入全域與 CLAUDE_CODE 工具設定」，再開始工作。**
   - **注意**：此報告僅在 Session 首次啟動對話時發出一次，後續問答切勿重複報告。

## Trigger A — 新專案（首次開啟）

偵測到專案內無 `.claude/` 設定時，執行：

1. 讀取 `~/.claude/skills/`，列出可用 skills。若未找到，詢問處理方式。
2. 確認摘要：列出啟用的 skills（例：Dev_Workflow、Quality_Guard）。
3. 詢問目前任務或目標。

## Trigger B — 現有專案（後續 session）

1. 重新載入 `~/.claude/skills/`（全域，原生自動列）。**專案 skill 一律放專案內 `._agents/skills/`**——原生清單不含此目錄，進專案時主動列其 SKILL.md 名稱＋描述（lazy）；優先於全域同名。若未找到，詢問處理方式。
2. 簡述啟用規則（例：`[Dev_Workflow 啟用中] [Quality_Guard 啟用中]`）。
3. 詢問目前任務或目標。

## 任務通訊協議執行

- **身為 Execution Agent（執行層）**：**僅在 AGENT_SPEC 明確要求時**才於完成後寫入 `AGENT_SIGNAL.log`。
  - 格式：`DONE|Claude|<FileName>|<Timestamp>`
  - 獨立小任務、自主分析、非派發工作不需寫入。
- **身為 Tech Lead（指揮層）**：無須寫入 `DONE` 訊號。負責發送 `REQUEST` 信號與持續監控 `AGENT_SIGNAL.log`，並在驗收通過後回寫 `VERIFIED` 信號。

## 同 repo 多 Claude CLI 並行（git worktree 隔離）

> 來源：attendance-dashboard 2026-06-22 實戰彙整。

- **各自建獨立 worktree＋分支**：同一個 repo 有多個 Claude CLI 同時工作時，每個各自 `git worktree add <dir> <branch>` 建獨立目錄與分支，working tree／index 完全隔離，互不踩 `git add`／不會吞掉彼此 staged 內容（解 index 全 repo 共用的撞車問題）。
- **共用紀錄檔各寫各的新檔**：TaskLog／lessons／INDEX 等共用文件改「各寫各的新檔」（依日期/主題/byline 區分），避免同檔 merge 衝突；確需共寫時最小插入＋帶 byline。
- **完工各自 merge main，後者先 pull**：各 worktree 完成後 merge 回 main；後 merge 的一方先 `git pull`／處理衝突再合，避免覆蓋先合者。

## Monitor 工具

- 監聽 log 檔時用 `tail -n 0 -f` 而非 `tail -f` : `tail -f` 啟動時會先顯示最後 10 行，每次 log 被 append 就可能重播舊紀錄；`-n 0` 只看新增內容。
- 一個 session 啟動一次 persistent Monitor 即可，不需每個任務重新啟動。

## ui-review：含進場動畫的頁面

- 有序列進場動畫（如英雄依序亮起）的頁面，Playwright 腳本必須等動畫跑完才能互動。
- 計算方式：`itemCount × intervalMs + buffer`（例：7 個英雄 × 260ms + 400ms buffer = 2220ms）。
- 若按鈕有 `pointer-events:none`（等狀態才開放），`page.click()` 會因 pointer-events 問題失敗；改用 `page.evaluate(() => el.click())` 繞過。
- 頁面用 transform `scale()` 縮放的整體舞台，子元素 `page.click()` 會被父層攔截（intercepts pointer events）；同樣改 `el.click()` 繞過。
- `waitUntil:"networkidle"` 遇到頁面載入 Google Fonts（或任何 CDN）常會卡到 30s timeout；改用 `domcontentloaded` + `waitForTimeout(700)`。
- 直書（`writing-mode:vertical-rl`）數欄數：逐字 `getBoundingClientRect` 不可靠；用 `range.selectNodeContents(el); range.getClientRects()`，每個 line box＝一欄。
- 手勢類功能（指標/觸控）用「合成事件＋API 強制切頁」的無頭測試容易「測過但實機失敗」，尤其右鍵 contextmenu 時序、pointer 捕獲——手勢務必請使用者實機驗，無頭只當煙霧測試。

## 前端互動手勢 / 資產路徑踩坑

- **相對資產路徑基準不同**：JS 字串裡的路徑（如 `img.src="../assets/x"`）相對「載入的 HTML 文件」解析；CSS `url("../assets/x")` 相對「CSS 檔自身」解析。扁平化或搬移目錄時兩者壞法不同——同一寫法可能 JS 壞而 CSS 正常，別一起盲改，先確認各自基準。
- **右鍵選單會吞掉指標事件**：右鍵拖曳手勢失效與「右鍵選單一直跳」常是同一個 bug——選單一彈出就接管輸入、攔截後續 pointermove/up。要用右鍵當觸發須先 `document.addEventListener("contextmenu", e=>e.preventDefault())`；kiosk 一律擋掉右鍵選單即可。
- **手勢中途開啟元素的誤觸**：在 pointermove 途中開啟覆蓋層（抽屜/選單），同一手勢結尾的 pointerup 會落在剛開的元素上、觸發它的 handler（誤選/誤關）。用「一次性旗標」消費下一個 pointerup，別用時間窗（慢速拖曳會超時失效）。
- **新手勢易撞既有同鍵拖曳**：頁面已有左鍵拖曳（如時間軸）時，新增左鍵手勢會互搶事件；改用右鍵可避開（但須配合上一條擋 contextmenu）。

## pptx / 簡報 版面對位

- **別硬從 OOXML XML 抽 layout 數值**：簡報常含 group transform（群組座標系）與多個同類文字框，直接讀 `off/ext`、`sz`、`lnSpc` 會量到互相矛盾的數字。
- 正解：`soffice --headless --convert-to pdf --outdir <dir> <檔>` 算繪成 PDF（macOS LibreOffice 在 `/Applications/LibreOffice.app/Contents/MacOS/soffice`），再 `pdftoppm -f N -l N -r 130 -png` 取出指定頁為高解析 PNG，對「算繪結果」做視覺／像素量測比對。
- CSS 直書踩坑：百分比 `padding` 是相對**容器寬度**算（非元素自身），書頁邊距要用固定 px；`height:100%+aspect-ratio` 會使尺寸隨容器浮動、量測不穩，改固定 px。

## gen 腳本與「只改 X」指令

- 用戶說「只改 X」時，**禁止重新執行 gen 腳本**產生整份文件——run gen script 等於覆蓋用戶對 Word 或腳本的其他所有改動。
- 正確做法：只改腳本中對應的那一筆資料，確認其他 ROWS 未動，再 run。若做不到「只動 X」，先問用戶，不要自行 run 整份。

## docx / OOXML 操作踩坑

- **python-docx buffer 限制**：大型複雜 docx（含圖、表格）用 python-docx 會失敗，必須改用 `lxml + huge_tree=True + zipfile` 直接操作 XML。
- **footnote ID 不可重複引用**：每個 `w:footnote/@w:id` 在 `document.xml` 只能有一個對應的 `w:footnoteReference`。若同一來源在多個表格都插入 fn_id，Word 會顯示「無法讀取的內容」並強制修復。解法：footnote 引用只放在詳細說明表格（Table[3/5]），分類總表（Table[1]）不加 fn_id。
- **ZIP 壓縮保留**：原始圖片等二進位檔為 `ZIP_STORED`；寫回時必須逐檔保留 `orig_info.compress_type`，不可全部改成 `ZIP_DEFLATED`。
