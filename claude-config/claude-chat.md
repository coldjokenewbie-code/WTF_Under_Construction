# Claude Chat 工具層設定
> 適用：claude.ai Chat（含 Projects）
> 載入方式：Chat Project instruction 中指定讀取此檔案 URL

---

## 工具特性與限制

- 無檔案系統、無 git 操作能力
- 可透過 WebFetch 讀取公開 URL（GitHub raw）
- 知識寫入需橋接：Chat 輸出 lesson 候選 → 使用者在 Claude Code 執行 `/lesson-add`
- Projects 提供跨 session 持久化（instruction + 上傳文件）

## 知識三層架構

| 層級 | 檔案位置 | 內容 |
|------|---------|------|
| 全域 | `claude-config/CLAUDE.md` | 所有工具共用原則 |
| 工具 | `claude-config/claude-chat.md`（本檔）| Chat 操作慣例 |
| 專案 | `chat-project-lessons/[專案名稱].md` | 各專案知識庫 |

## Session 開場協議

每次對話開始，確認已讀取：
1. 全域設定（CLAUDE.md）
2. 本檔案（claude-chat.md）
3. 若有專案：`chat-project-lessons/[專案名稱].md`

讀取完成後簡述：「已載入全域 + Chat 工具 + [專案名稱] 設定」，再詢問任務。

## Lesson 候選輸出格式

當 session 中出現值得保留的經驗，使用以下格式輸出（供使用者橋接到 `/lesson-add`）：

```
【Lesson 候選】
層級建議：全域 / 工具(chat) / 專案([專案名])
內容：[一句話，具體可執行的規則]
觀察來源：[這次發現此規則的情境]
```

## Session 結束協議

使用者說「本對話獲得經驗」或「lesson learned here」時，輸出本次對話值得保留的經驗（格式同上）。
使用者可直接複製後在 Claude Code 執行 `/lesson-add`。

---

## 累積 Lessons

> 此區塊由 `/lesson-add 工具 chat` 維護，記錄 Claude Chat 使用慣例。

<!-- lessons-start -->
**[2026-04-09] 對話過長時主動建議交接**
對話過長時 Claude 開始重複犯同樣的錯誤，應主動建議使用者開新對話並產出交接文件。
來源：固定值問題重複出現三次才被使用者指出。
<!-- lessons-end -->
