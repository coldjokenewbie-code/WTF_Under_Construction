# Claude Chat 工具層設定
> 適用：claude.ai Chat（含 Projects）
> 載入方式：固定規則內嵌 Project Instruction（由儀表板產生器維護）；本檔上傳至 Project Knowledge 供參考知識查詢

---

## 工具特性與限制

- 無檔案系統、無 git 操作能力
- 無法讀取外部 URL（raw.githubusercontent.com 不可靠）
- 知識寫入需橋接：Chat 輸出 Lesson 候選 → 使用者在 Claude Code 執行 `/lesson-add`
- Projects 提供跨 session 持久化（Project Instruction + 上傳文件）

## 知識三層架構

| 層級 | 存放位置 | Chat 讀取方式 |
|------|---------|--------------|
| 全域原則 | `claude-config/CLAUDE.md` | 內嵌 Project Instruction |
| Chat 固定規則 | 本檔 `## 固定規則` 段落 | 內嵌 Project Instruction（由儀表板產生器維護）|
| Chat 參考知識 | 本檔 `## 參考知識` 段落 | 上傳至 Project Knowledge |
| 專案知識庫 | `chat-project-lessons/[專案名稱].md` | 上傳至 Project Knowledge |

## Lesson 候選輸出格式

當 session 中出現值得保留的經驗，輸出以下格式（供使用者橋接到 `/lesson-add`）：

```
【Lesson 候選】
層級建議：全域 / 工具(chat) rule / 工具(chat) kb / 專案([專案名])
內容：[一句話，具體可執行的規則]
觀察來源：[這次發現此規則的情境]
```

## Session 結束協議

使用者說「本對話獲得經驗」或「lesson learned here」時，輸出本次對話值得保留的經驗（格式同上）。
使用者複製後在 Claude Code 執行 `/lesson-add`。

---

## 固定規則

> 此區塊由 `/lesson-add 工具 chat rule` 維護。同步寫入 dashboard.html 產生器，需重新複製 Project Instruction 貼回 claude.ai。

<!-- rules-start -->
- 對話過長時（超過 30 來回或開始重複犯同樣錯誤），主動建議開新對話並產出交接文件。
- 開場確認專案範圍，若有 PRD，詢問使用者提供後再接任務，避免遺漏模組。
<!-- rules-end -->

## 參考知識

> 此區塊由 `/lesson-add 工具 chat kb` 維護。更新後需重新上傳本檔至 Project Knowledge。

<!-- kb-start -->
**[2026-04-09] GIF 錄製避免 gif.js**
gif.js 在 file:// 或受限環境因 CORS 靜默失敗卡死；改用原生 `MediaRecorder + canvas.captureStream()` 零等待解決。
來源：錄製後卡在 encoding GIF 超過 10 分鐘無進度。
<!-- kb-end -->
