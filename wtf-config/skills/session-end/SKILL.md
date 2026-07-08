---
name: session-end
description: 產出工作紀錄、呼叫 lesson-add 萃取教訓、commit 並 merge 至 main。
---

# Session End

執行以下步驟，不需逐步確認：

1. **產出/更新工作紀錄 (TaskLog)**：
   - 在 `_context/` 下建立或更新 `TaskLog_YYYY-MM-DD_[當前主題].md`（依 `rules`／GLOBAL.md 命名慣例，不用 `WorkLog_` 等通用名）。
   - 記錄本次 Session 完成項目、未解決問題與下一步建議。
   - 任務若已結案：依 GLOBAL.md「結案歸檔」規則改前綴 `ClosedTaskLog_` 並移入 `_context/archive/`。

2. **執行 `lesson-add`（更新教訓）**：
   - 讀取 `_context/lessons-learned.md`（不存在則建立）。
   - 呼叫 `lesson-add` 邏輯，從本次對話萃取有價值的教訓（錯誤修正、新規則、流程改善），追加至檔案中。

3. **清理視覺驗證擷圖**：
   - AI 工作過程用於視覺驗證的擷圖屬暫時性產物，結案時一律清除，不入 commit、不長期堆積。
   - 清除範圍：本專案 `outputs/_shared/_screenshots/` 下本次工作產生的擷圖（含各區子夾如 `_screenshots/ebook/`）。
   - **保留例外**：已被 TaskLog／審查文件／交付物**引用**的圖，或使用者明確指定保留者，不刪。不確定是否被引用先 grep 檔名，再決定。
   - 刪除前列出將清除的檔案清單；只清 `outputs/_shared/_screenshots/`，不碰 `outputs/<子專案>/` 內正式產出與 `archive/`。

4. **合併與推送 (`merge-main`)**：
   - 執行 `/merge-main` 將本次產出 commit、push 並 merge 至 main 分支。

5. **回報摘要**：
   - 在對話中回報本次 Session 簡短摘要（3-5 條）。
