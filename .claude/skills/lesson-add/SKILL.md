---
name: lesson-add
description: 將觀察整合進 CLAUDE.md，並檢視全文去除矛盾與冗餘，精簡後存檔。用法：/lesson-add [層級] [內容]
---

# Lesson Add

用法：`/lesson-add [層級] [觀察內容]`

層級：
- `專案` → 當前專案根目錄的 `.claude/CLAUDE.md`
- `全域` → `~/.claude/CLAUDE.md`（所有專案共用）
- `工具` → 對應工具設定段落（Claude Code / Cowork）

執行步驟：

1. 依層級讀取對應 CLAUDE.md。

2. 將觀察整合進最相關的既有段落（不新增段落，除非真的無處安放）。

3. 檢視整份 CLAUDE.md：
   - 互相矛盾 → 保留較新、較具體的版本
   - 重複或疊床架屋 → 合併或刪除
   - 過時內容 → 移除
   - 每條規則能否一句話說清楚 → 精簡

4. 存檔：
   - `專案` → 只更新當前專案的 `.claude/CLAUDE.md`
   - `全域` → 更新 `~/.claude/CLAUDE.md`

5. Commit 並 push（專案層級）：
   ```
   git add .claude/CLAUDE.md
   git commit -m "lesson-add(專案): [一句話摘要]"
   git push
   ```
   全域層級直接更新 `~/.claude/CLAUDE.md`，無需 git commit。

6. 回報：新增了什麼、刪除或合併了什麼、精簡前後行數變化。
