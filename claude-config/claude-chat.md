# Claude Chat 工具層設定
> 適用：claude.ai Chat（含 Projects）
> 載入方式：Chat Project instruction 中指定讀取此檔案 URL

---

## 工具特性與限制

- 無檔案系統、無 git 操作能力
- 可透過 WebFetch 讀取公開 URL（GitHub raw）
- 知識寫入需橋接：Chat 輸出 lesson 候選 → 使用者在 Claude Code 執行 `/lesson-add`
- Projects 提供跨 session 持久化（instruction + 上傳文件）

## Session 開場協議

每次對話開始，確認已讀取：
1. 全域設定（CLAUDE.md）
2. 本檔案（claude-chat.md）
3. 若有專案：該專案的 lesson 檔案（由 Project instruction 指定）

讀取完成後簡述：「已載入全域設定 + Chat 工具設定」，再詢問任務。

## Lesson 候選輸出格式

當 session 中出現值得保留的經驗，使用以下格式輸出（供使用者橋接到 `/lesson-add`）：

```
【Lesson 候選】
層級建議：全域 / 工具(chat) / 專案([專案名])
內容：[一句話，具體可執行的規則]
觀察來源：[這次發現此規則的情境]
```

## Session 結束協議

對話結束前，若有值得保留的經驗，主動輸出 lesson 候選清單（格式同上）。
使用者可直接複製後在 Claude Code 執行 `/lesson-add`。

---

## 累積 Lessons

> 此區塊由 `/lesson-add 工具 chat` 維護，記錄 Claude Chat 使用慣例。

<!-- lessons-start -->
（目前尚無 lesson，第一條 lesson 將從使用中累積）
<!-- lessons-end -->
