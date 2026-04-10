---
name: session-end
description: commit 本次產出並 merge 到 main。儀表板與 lessons 由 Nightly 自動處理。
---

# Session End

執行以下步驟，不需逐步確認：

1. Commit 所有變更：
   ```
   git add -A
   git commit -m "session-end: [日期] [本次主要產出一句話摘要]"
   git push
   ```

2. 執行 `/merge-main` 將變更合併到 main。

3. 回報本次 session 摘要（3-5 條）。

> 儀表板討論記錄、lesson-add 由凌晨 Nightly 自動從 transcript 處理，無需手動執行。
