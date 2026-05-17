# Claude Code 工具層設定
> 適用：Claude Code CLI / IDE Extension
> 載入方式：`~/.claude/CLAUDE.md` 指向此檔；本機自動載入

## Trigger A — 新專案（首次開啟）

偵測到專案內無 `.claude/` 設定時，執行：

1. 讀取 `~/.claude/skills/`，列出可用 skills。若未找到，詢問處理方式。
2. 確認摘要：列出啟用的 skills（例：Dev_Workflow、Quality_Guard）。
3. 詢問目前任務或目標。

## Trigger B — 現有專案（後續 session）

1. 重新載入 `~/.claude/skills/`（或 `.claude/skills/`，優先用專案層級）。若未找到，詢問處理方式。
2. 簡述啟用規則（例：`[Dev_Workflow 啟用中] [Quality_Guard 啟用中]`）。
3. 詢問目前任務或目標。

## 溝通慣例與意圖解讀

1. 使用者以繁體中文（台灣用語）溝通。短指令（如座標、表單 ID、「長這樣」）視為字面意義直接執行，不重新詮釋、不捨棄。真正模糊才詢問，其餘不問。
2. 以「簡介」、「說明」、「討論」開頭的輸入，只討論不改動——確認決定後再執行。
3. 「更新儀表板」隱含「merge main」——使用者說要更新儀表板，代表要看到結果，執行後必須 merge main。
4. 使用者要求「做到好再交付／給我驗收」時，代表 Agent 必須自行反覆檢查、修正、驗證到符合需求為止；若自查不符合，就繼續修改，不提交給使用者處理。沒有先檢視就回報完成，等同把驗收成本丟給使用者，禁止。

## 截圖與圖片

GIF 格式與過大圖片（實測曾卡死 session）建議避免使用；改貼 PNG/JPG 或文字描述。PNG/JPG 上限約 5MB。

## 程式編輯

主要語言：TypeScript、HTML、Python。UI 編輯採增量修改，每次只動一個元素。修改後確認 nav bar 與版面框架完整保留。

## UI 樣式修改

字體大小每次只調 1-2px。套用前若幅度較大須確認。禁止連帶修改未被要求的元素。

## ui-review：含進場動畫的頁面

- 有序列進場動畫（如英雄依序亮起）的頁面，Playwright 腳本必須等動畫跑完才能互動。
- 計算方式：`itemCount × intervalMs + buffer`（例：7 個英雄 × 260ms + 400ms buffer = 2220ms）。
- 若按鈕有 `pointer-events:none`（等狀態才開放），`page.click()` 會因 pointer-events 問題失敗；改用 `page.evaluate(() => el.click())` 繞過。

## docx / OOXML 操作踩坑

- **python-docx buffer 限制**：大型複雜 docx（含圖、表格）用 python-docx 會失敗，必須改用 `lxml + huge_tree=True + zipfile` 直接操作 XML。
- **footnote ID 不可重複引用**：每個 `w:footnote/@w:id` 在 `document.xml` 只能有一個對應的 `w:footnoteReference`。若同一來源在多個表格都插入 fn_id，Word 會顯示「無法讀取的內容」並強制修復。解法：footnote 引用只放在詳細說明表格（Table[3/5]），分類總表（Table[1]）不加 fn_id。
- **ZIP 壓縮保留**：原始圖片等二進位檔為 `ZIP_STORED`；寫回時必須逐檔保留 `orig_info.compress_type`，不可全部改成 `ZIP_DEFLATED`。
