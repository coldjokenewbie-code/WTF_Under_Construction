---
name: resume-id-info
description: 工作到一半不想中斷（例如 cmux 一直提醒更新、想把背景 session 獨立標出來）時，快速把目前 session id 記進當前 TaskLog，供之後任一新 session 手動接續。用法：/resume-id-info [備註]。純手動，不做自動偵測或 hook 提醒。
---

# /resume-id-info — 標記目前 session 供之後接續

用法：`/resume-id-info [備註]`（備註可省略）

適用情境：工作進行中、還沒到可以 `/session-end` 收尾的段落，但預期可能要中斷這個 process（cmux 提醒更新、想把背景 session 獨立標出來留著之後接）——**由使用者自己判斷是否要標記，不做任何自動偵測**。若已經到一個段落、要正常收尾，直接用 `/session-end`，不用本 skill。

## 標記（寫入）

1. **取得 session id**：Bash 執行 `echo $CLAUDE_CODE_SESSION_ID`。
2. **備註**：使用者有給就用使用者的話；沒給就自己用一句話概括「目前正在做什麼」（不用回頭問使用者，降低打字量是本 skill 的重點）。
3. **寫入位置**：當前專案 `_context/INDEX.md` 指到的**當前 TaskLog** 檔案最上方，一個固定小節，不存在就新建、存在就 append 一行（可多筆並存，互不覆蓋）：
   ```
   ## ⏸ 待續 session
   - `<session_id>` ｜ <YYYY-MM-DD HH:MM> ｜ <備註>
   ```
4. **回報**：一句話——已標記，session_id 前 8 碼＋備註。不用 commit／push（TaskLog 本來就會在下次 `/session-end` 時一併處理）。

## 接續（讀取，純手動觸發）

沒有自動提醒機制。使用者開新 session 想接續時，會自己叫這輪 session 去看（例如「看一下有沒有待續 session」）。收到這類要求時：

1. 讀當前 TaskLog 的「## ⏸ 待續 session」小節，列出所有未消化紀錄（session_id＋時間＋備註）。
2. 使用者選定要接續的那筆 → 告知：`/resume` 本質是終止目前 process、重啟新 process，本 session 無法在對話中直接接手，需使用者自己執行 `claude --resume <session_id>`（或不帶參數跑 `/resume` 挑 picker）。
3. **不論使用者最後接不接續，該筆紀錄問完就從 TaskLog 該小節刪除**；其餘未問到的紀錄不動。
4. 若小節清空，移除整個「## ⏸ 待續 session」標題本身，不留空節。

## 注意事項

- 純手動：不掛 SessionStart hook，不做「這個 session 是不是異常結束」的判斷——crash／終端機被關掉不影響 transcript，Claude Code 本身就保留 30 天可 `--resume` 撿回，不需要本 skill 處理那個情境。
- 本 skill 只負責「使用者主動想留的接續點」，跟 `/session-end`（正式收尾：TaskLog＋lessons＋commit＋push）是互斥情境，不要混用。
