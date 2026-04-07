---
name: lesson-add
description: 將觀察整合進 CLAUDE.md，並檢視全文去除矛盾與冗餘，精簡後存檔。用法：/lesson-add [層級] [內容]
---

# Lesson Add

用法：`/lesson-add [層級] [觀察內容]`

層級：
- `全域` → `~/.claude/CLAUDE.md` + `claude-config/CLAUDE.md`
- `工具` → 對應工具段落（Claude Code / Cowork / Chat）

執行步驟：

1. 讀取對應 CLAUDE.md。

2. 將觀察整合進最相關的既有段落（不新增段落，除非真的無處安放）。

3. 檢視整份 CLAUDE.md：
   - 互相矛盾 → 保留較新、較具體的版本
   - 重複或疊床架屋 → 合併或刪除
   - 過時內容 → 移除
   - 每條規則能否一句話說清楚 → 精簡

4. 同步更新兩份（`~/.claude/CLAUDE.md` + GitHub repo 的 `claude-config/CLAUDE.md`）。

5. Commit 並 push：
   ```
   git add claude-config/CLAUDE.md
   git commit -m "lesson-add: [一句話摘要]"
   git push
   ```

6. 回報：新增了什麼、刪除或合併了什麼、精簡前後行數變化。
