---
name: session-end
description: 產出工作紀錄、呼叫 lesson-add 萃取教訓、commit 並 merge 至 main。
---

# Session End

執行以下步驟，不需逐步確認：

1. **產出/更新工作紀錄 (WorkLog)**：
   - 在 `_context/` 下建立或更新 `WorkLog_YYYY-MM-DD_[當前主題].md`。
   - 記錄本次 Session 完成項目、未解決問題與下一步建議。

2. **執行 `lesson-add`（更新教訓）**：
   - 讀取 `_context/lessons-learned.md`（不存在則建立）。
   - 呼叫 `lesson-add` 邏輯，從本次對話萃取有價值的教訓（錯誤修正、新規則、流程改善），追加至檔案中。

3. **合併與推送 (`merge-main`)**：
   - 執行 `/merge-main` 將本次產出 commit、push 並 merge 至 main 分支。

4. **回報摘要**：
   - 在對話中回報本次 Session 簡短摘要（3-5 條）。
