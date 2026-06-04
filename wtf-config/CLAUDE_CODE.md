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

1. 重新載入 `~/.claude/skills/`（或 `.claude/skills/`，優先用專案層級）。若未找到，詢問處理方式。
2. 簡述啟用規則（例：`[Dev_Workflow 啟用中] [Quality_Guard 啟用中]`）。
3. 詢問目前任務或目標。

## 任務通訊協議執行

- **身為 Execution Agent（執行層）**：**僅在 AGENT_SPEC 明確要求時**才於完成後寫入 `AGENT_SIGNAL.log`。
  - 格式：`DONE|Claude|<FileName>|<Timestamp>`
  - 獨立小任務、自主分析、非派發工作不需寫入。
- **身為 Tech Lead（指揮層）**：無須寫入 `DONE` 訊號。負責發送 `REQUEST` 信號與持續監控 `AGENT_SIGNAL.log`，並在驗收通過後回寫 `VERIFIED` 信號。

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
