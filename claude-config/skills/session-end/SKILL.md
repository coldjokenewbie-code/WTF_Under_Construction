---
name: session-end
description: commit 本次產出、更新 lessons-learned、merge 到 main。
---

# Session End

執行以下步驟，不需逐步確認：

1. 執行 `/merge-main`（含 commit、push、merge 到 main）。

2. 更新 lessons-learned：
   - 讀取 `_context/lessons-learned.md`（不存在則建立）
   - 從本次 session 萃取值得記錄的教訓（錯誤修正、新發現的規則、流程改善）
   - 將新教訓追加進檔案，已有的不重複
   - 存檔

3. 回報本次 session 摘要（3-5 條）。
