# Office 文件（pptx／docx／gen 腳本）踩坑集
> 適用：處理簡報、Word、OOXML、生成腳本時開啟；平時不載入
> 來源：原 CLAUDE_CODE.md 抽出（2026-07-03），內容為歷次實戰教訓

## pptx／簡報版面對位

- **別硬從 OOXML XML 抽 layout 數值**：簡報常含 group transform（群組座標系）與多個同類文字框，直接讀 `off/ext`、`sz`、`lnSpc` 會量到互相矛盾的數字。
- 正解：`soffice --headless --convert-to pdf --outdir <dir> <檔>` 算繪成 PDF（macOS LibreOffice 在 `/Applications/LibreOffice.app/Contents/MacOS/soffice`），再 `pdftoppm -f N -l N -r 130 -png` 取出指定頁為高解析 PNG，對「算繪結果」做視覺／像素量測比對。
- CSS 直書踩坑：百分比 `padding` 是相對**容器寬度**算（非元素自身），書頁邊距要用固定 px；`height:100%+aspect-ratio` 會使尺寸隨容器浮動、量測不穩，改固定 px。

## gen 腳本與「只改 X」指令

- 用戶說「只改 X」時，**禁止重新執行 gen 腳本**產生整份文件——run gen script 等於覆蓋用戶對 Word 或腳本的其他所有改動。
- 正確做法：只改腳本中對應的那一筆資料，確認其他 ROWS 未動，再 run。若做不到「只動 X」，先問用戶，不要自行 run 整份。

## docx／OOXML 操作踩坑

- **python-docx buffer 限制**：大型複雜 docx（含圖、表格）用 python-docx 會失敗，必須改用 `lxml + huge_tree=True + zipfile` 直接操作 XML。
- **footnote ID 不可重複引用**：每個 `w:footnote/@w:id` 在 `document.xml` 只能有一個對應的 `w:footnoteReference`。若同一來源在多個表格都插入 fn_id，Word 會顯示「無法讀取的內容」並強制修復。解法：footnote 引用只放在詳細說明表格（Table[3/5]），分類總表（Table[1]）不加 fn_id。
- **ZIP 壓縮保留**：原始圖片等二進位檔為 `ZIP_STORED`；寫回時必須逐檔保留 `orig_info.compress_type`，不可全部改成 `ZIP_DEFLATED`。
