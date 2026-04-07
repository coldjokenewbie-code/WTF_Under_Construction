---
name: merge-main
description: 將當前分支 merge 到 main 並 push。每個獨立任務完成後立即執行，避免衝突累積。
---

# Merge Main

執行以下步驟：

1. 確認當前分支有無未 commit 的變更：
   ```
   git status
   ```
   若有，先 commit：
   ```
   git add -A
   git commit -m "[描述本次變更]"
   git push
   ```

2. 切換到 main 並同步遠端：
   ```
   git checkout main
   git pull --rebase origin main
   ```

3. Merge 當前功能分支：
   ```
   git merge [分支名稱]
   ```
   若有衝突，優先保留功能分支的版本（`git checkout --theirs`），解完後繼續。

4. Push 到遠端 main：
   ```
   git push origin main
   ```

5. 切回功能分支繼續工作：
   ```
   git checkout [分支名稱]
   ```

6. 回報：merge 完成，main 已更新。
