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

## 檔案存取（FSA）——存檔預設路徑

規則本文在 `GLOBAL.md`「工作品質底線」的「存檔預設路徑鐵律」。以下是寫法與踩過的坑。

- **預設位置怎麼指**：`showSaveFilePicker({ suggestedName, startIn })`、`showDirectoryPicker({ startIn, mode:'readwrite' })`。`startIn` 收兩種值——先前存下的 `FileSystemHandle`（最精確，直接開在那個資料夾），或具名位置字串 `'documents' | 'downloads' | 'desktop' | 'pictures' | 'music' | 'videos'`。**沒有辦法用字串路徑指定任意資料夾**，這是瀏覽器的安全限制，所以第一次一定得由使用者選一次。
- **第一次選完就別再問**：把回傳的 handle 存進 IndexedDB（handle 可被 structured-clone），下次直接 `handle.createWritable()` 寫回同一檔；只需先 `handle.requestPermission({mode:'readwrite'})` 確認權限沒過期。同一組 picker 也可帶 `id:'<用途代號'`，瀏覽器會記住該 id 上次開啟的位置。
- **`startIn` 帶 handle 前要先確認它還活著**：權限被撤銷或檔案被刪後，handle 仍在 IndexedDB 但 `queryPermission` 會回 `prompt`／開啟時丟錯。一律 try/catch，失敗就退回重新選檔，別讓整個存檔流程掛掉。
- **必須由使用者手勢觸發**：`showSaveFilePicker`／`showDirectoryPicker` 只能在 click 之類的手勢事件裡呼叫。放在 `await` 之後（尤其是先 await 了 IndexedDB 或 fetch）常會失去手勢資格，報 `Failed to execute 'showDirectoryPicker' on 'Window'`／`must be handling a user gesture`。**先開 picker、再做非同步準備**，順序不能顛倒。
- **同一時間只能開一個 picker**：前一個還沒關就再呼叫會直接丟錯（訊息同上）。按鈕要在開啟期間 disable。
- **取消不是錯誤**：使用者關掉選擇器會丟 `AbortError`，要靜默處理，不可當成失敗跳警告。
- **不支援時的降級**：Safari 與多數行動瀏覽器沒有 FSA。降級為 `<a download>` 下載，並在畫面明示「請把檔案放回 ○○ 資料夾」。
- **不要用 `startIn:'documents'` 當保底**（2026-08-27 PO 裁定）：那等於把使用者丟到系統「文件」夾，離目標資料夾更遠。沒有可用 handle 時**寧可不給 `startIn`**，另外提供一顆「複製資料夾路徑」按鈕：使用者複製後在對話框按 **⌘⇧G**（Windows：在檔名欄貼完整路徑）一步跳到目標夾。這是目前唯一能把「首次那一次選檔」壓成一個動作的作法。
- **檢核／勾選類頁面的語意是「覆蓋原檔」**：狀態檔要跟頁面放同一夾並隨頁面一起交付，按鈕寫「存檔（覆蓋本資料夾原檔）」。若狀態只存 localStorage、不落檔，換機器或清快取就全沒了——把已定案的勾選結果**內建進 HTML**（如 `data-done="1"`），localStorage／狀態檔存在時才覆寫，這樣任何人打開看到的都是同一份現況。
- **handle 要在載入時預讀成變數**：`click` 內才 `await getHandle()` 會失去手勢資格（同上一條「必須由使用者手勢觸發」）。正確順序＝頁面載入時 `getHandle().then(h=>cached=h)`，click 內若 `cached` 存在就直接 `createWritable()`、完全不開 picker；沒有才同步呼叫 picker。
