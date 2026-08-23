# Office 文件（pptx／docx／表格匯出／gen 腳本）踩坑集
> 適用：處理簡報、Word、OOXML、Excel／CSV 匯出、生成腳本時開啟；平時不載入
> 來源：原 CLAUDE_CODE.md 抽出（2026-07-03），內容為歷次實戰教訓

## 表格資料匯出（Excel／CSV）——預設格式

要求「做成 Excel」時，除非對方明講要 `.xlsx`，一律輸出 **CSV**：

| 項目 | 規格 | 原因 |
|---|---|---|
| 編碼 | UTF-8 **with BOM**（`\xef\xbb\xbf` 開頭） | **Windows 版 Excel 沒有 BOM 會把中文顯示成亂碼**，是最常見的交付事故 |
| 行尾 | CRLF | 交付對象多為 Windows |
| 跳脫 | 值含逗號／雙引號／換行時整格加雙引號，內部雙引號改兩個 | 否則欄位錯位 |

- 不預設 `.xlsx`：需額外套件、**openpyxl 存檔會丟失 drawings**（改既有 xlsx 得走 zip 層外科手術）；CSV 是純文字，可版控、可 diff、可程式驗證。對方要 xlsx 再用 `soffice --headless --convert-to xlsx` 由 CSV 轉出，不手工維護兩份。
- **產 CSV 一律 `open(..., encoding='utf-8')` 直接寫檔，不經 stdout**——Windows 主控台 CP950 會毒化輸出（`UnicodeEncodeError` 或亂碼）。
- **產出後必驗三項，缺一不可**：
  1. 機檢 BOM 與 CRLF（`raw[:3]==b'\xef\xbb\xbf'`）
  2. 機檢欄數一致（`len({len(r) for r in csv.reader(...)})==1`）
  3. **實際用試算表開啟看中文**（`soffice --headless --convert-to xlsx` 後讀回）——BOM 對不代表跳脫對，第 3 項不可省。

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

- **openpyxl 不可回寫含繪圖物件的 xlsx**（2026-08-14 南科再生水廠）：檔內 `xl/drawings/` 有東西時，openpyxl 開檔存檔會破壞 drawing 與字串表，Excel 報錯無法修復。防：動手前 `unzip -l` 查 drawings；有圖→內容另開獨立新檔或 zip 層只改單一 sheet XML；改前必備份（Excel 自存的版本才保證健康）。

## pptx「已修復」對話框——LibreOffice／ElementTree 全過但 PowerPoint 判損毀（2026-08-24 南科再生水廠）

python-pptx／XML 手改產出的 pptx，LibreOffice 轉檔與 ElementTree 解析都過，但 PowerPoint 嚴格驗證仍判損毀、跳「已修復，已移除部分內容」——PO 若存檔即污染正式檔。已實證四類根因，動手刪頁／刪 shape／改 rPr 前逐條核對：

1. **`p14:sectionLst` 懸空 sldId**：複製母檔刪頁後，`presentation.xml` 的 `p14:sectionLst`（章節 extLst）內 `p14:sldId` 未同步移除——python-pptx `drop_rel`＋`sldIdLst.remove()` 只動主清單，不動 extLst。刪頁後必須另外掃 `p14:sectionLst` 清懸空 id。
2. **`<p:timing>` 動畫樹指向已刪 shape**：保留頁若含動畫，`p:timing` 樹的 `spTgt`／`@spid` 可能指向已刪除的影片或動畫 shape——刪 shape 時只清了 `spTree` 與 `.rels`，沒清 timing 樹。刪 shape 前先查該頁 `p:timing` 有無引用該 shape id，一併清除。
3. **`docProps/app.xml` 過時快取**：Slides 數、`HeadingPairs`／`TitlesOfParts` 未隨刪頁／刪 shape 同步更新，PowerPoint 開檔比對快取與實際內容不符即判損毀。改動頁數或大綱結構後必須重算 app.xml。
4. **`a:rPr` 子元素順序錯誤**：手塞 XML 時，`a:rPr` 的子元素有規定順序（`ln→...→latin→ea→cs→sym→hlinkClick→hlinkMouseOver→...→extLst`），直接 `append()` 新元素幾乎必踩破壞順序。改用「先定位既有序列中的插入點」而非 append 到尾端。

**偵測缺口**：LibreOffice 轉檔忽略未知 ext 元素與子元素順序、ElementTree 只驗 well-formed（合法 XML）——兩者都**不是** PowerPoint 相容性的證據，通過這兩關不代表 PowerPoint 不會判損毀。真正閘門＝**PowerPoint 實際開啟無「已修復」對話框**（macOS 需自動化權限跑 AppleScript／COM 自動開檔驗證；權限被拒時退而由使用者目視開啟確認，不可用 LibreOffice／ElementTree 結果替代回報「已驗證」）。

**參考實作**：南科再生水廠專案 `tools/_shared/pptx_postprocess.py`——`postprocess()` 修①②③（sectionLst 懸空清除、timing 樹清除、app.xml 重算），`verify()` 四查（含①②③＋rPr 子元素順序＋zip 內重複項＋XML 解析），CLI 回傳碼 0＝PASS。跨專案處理 pptx 刪頁／刪 shape／手改 XML 時，優先取用或比照此腳本邏輯，不要重新摸索。

**docx 類比**：同族問題原則相同——刪內容（樣式、編號清單、footnote）後，任何「引用」都要重掃一遍「引用集合 ⊆ 存在集合」，不能只驗刪除動作本身成功。
