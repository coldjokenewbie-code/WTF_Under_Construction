---
name: session-end
description: 整理本次 session 產出，更新 WTF 儀錶板與討論記錄，commit 並 push。
---

# Session End

執行以下步驟，不需逐步確認：

1. 列出本次 session 的主要產出：
   - 新增或修改的檔案
   - 重要決策
   - 未完成項目

2. 更新 `dashboard.html`：
   - 在「討論記錄」加入今天的 log-item（日期、標題、重點條列）
   - 將新的未完成項目加入待辦清單
   - 將已完成項目標為 done

3. Commit 所有變更：
   ```
   git add -A
   git commit -m "session-end: [日期] [本次主要產出一句話摘要]"
   git push
   ```

4. 執行 `/merge-main` 將變更合併到 main。

5. 回報本次 session 摘要（3-5 條）。
