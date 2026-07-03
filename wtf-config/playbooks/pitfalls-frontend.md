# 前端／Playwright 驗收踩坑集
> 適用：ui-review、網頁互動、手勢、資產路徑相關工作時開啟；平時不載入
> 來源：原 CLAUDE_CODE.md 抽出（2026-07-03），內容為歷次實戰教訓

## ui-review：含進場動畫的頁面

- 有序列進場動畫（如英雄依序亮起）的頁面，Playwright 腳本必須等動畫跑完才能互動。
- 計算方式：`itemCount × intervalMs + buffer`（例：7 個英雄 × 260ms + 400ms buffer = 2220ms）。
- 若按鈕有 `pointer-events:none`（等狀態才開放），`page.click()` 會因 pointer-events 問題失敗；改用 `page.evaluate(() => el.click())` 繞過。
- 頁面用 transform `scale()` 縮放的整體舞台，子元素 `page.click()` 會被父層攔截（intercepts pointer events）；同樣改 `el.click()` 繞過。
- `waitUntil:"networkidle"` 遇到頁面載入 Google Fonts（或任何 CDN）常會卡到 30s timeout；改用 `domcontentloaded` + `waitForTimeout(700)`。
- 直書（`writing-mode:vertical-rl`）數欄數：逐字 `getBoundingClientRect` 不可靠；用 `range.selectNodeContents(el); range.getClientRects()`，每個 line box＝一欄。
- 手勢類功能（指標/觸控）用「合成事件＋API 強制切頁」的無頭測試容易「測過但實機失敗」，尤其右鍵 contextmenu 時序、pointer 捕獲——手勢務必請使用者實機驗，無頭只當煙霧測試。

## 前端互動手勢／資產路徑

- **相對資產路徑基準不同**：JS 字串裡的路徑（如 `img.src="../assets/x"`）相對「載入的 HTML 文件」解析；CSS `url("../assets/x")` 相對「CSS 檔自身」解析。扁平化或搬移目錄時兩者壞法不同——同一寫法可能 JS 壞而 CSS 正常，別一起盲改，先確認各自基準。
- **右鍵選單會吞掉指標事件**：右鍵拖曳手勢失效與「右鍵選單一直跳」常是同一個 bug——選單一彈出就接管輸入、攔截後續 pointermove/up。要用右鍵當觸發須先 `document.addEventListener("contextmenu", e=>e.preventDefault())`；kiosk 一律擋掉右鍵選單即可。
- **手勢中途開啟元素的誤觸**：在 pointermove 途中開啟覆蓋層（抽屜/選單），同一手勢結尾的 pointerup 會落在剛開的元素上、觸發它的 handler（誤選/誤關）。用「一次性旗標」消費下一個 pointerup，別用時間窗（慢速拖曳會超時失效）。
- **新手勢易撞既有同鍵拖曳**：頁面已有左鍵拖曳（如時間軸）時，新增左鍵手勢會互搶事件；改用右鍵可避開（但須配合上一條擋 contextmenu）。
