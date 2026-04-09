---
name: lesson-add
description: 將觀察整合進對應層級的設定檔，去冗餘後存檔。用法：/lesson-add [層級] [內容]
---

# Lesson Add

用法：`/lesson-add [層級] [觀察內容]`

層級：
- `專案` → 當前專案根目錄的 `.claude/CLAUDE.md`（Claude Code 專案）
- `專案 chat [專案名稱]` → `chat-project-lessons/[專案名稱].md`（Chat 專案知識庫）
- `全域` → `~/.claude/CLAUDE.md`（所有工具共用）+ `claude-config/CLAUDE.md`（WTF repo 同步）
- `工具 chat` → `claude-config/claude-chat.md` 的 `<!-- lessons-start/end -->` 區塊
- `工具 cowork` → `claude-config/cowork.md`
- `工具 code` → `claude-config/claude-code.md`

## 層級分析（自動判斷，可覆寫）

收到內容後先判斷適合層級：

| 若內容描述的是… | 建議層級 |
|---|---|
| Claude Code 專案的業務邏輯、檔案結構 | 專案 |
| Chat 專案的業務邏輯、操作慣例 | 專案 chat [專案名稱] |
| Claude Chat 的操作慣例、UI 行為、session 流程 | 工具 chat |
| Cowork 的 agent 行為、沙盒限制 | 工具 cowork |
| Claude Code 的檔案操作、git 流程 | 工具 code |
| 跨工具都適用的溝通原則、思考框架 | 全域 |

若判斷層級與使用者指定不同，說明建議後詢問確認。

## 執行步驟

1. 依層級讀取對應檔案。

2. 將觀察整合進最相關的既有段落（不新增段落，除非真的無處安放）。
   - `工具 chat` / `專案 chat`：寫入 `<!-- lessons-start -->` 和 `<!-- lessons-end -->` 之間。

3. 檢視整份檔案：
   - 互相矛盾 → 保留較新、較具體的版本
   - 重複或疊床架屋 → 合併或刪除
   - 過時內容 → 移除
   - 每條規則能否一句話說清楚 → 精簡

4. 存檔並 commit + push：

   **專案層（Claude Code）**：
   ```
   git add .claude/CLAUDE.md
   git commit -m "lesson-add(專案): [一句話摘要]"
   git push
   ```

   **專案層（Chat）**：
   ```
   git add chat-project-lessons/[專案名稱].md
   git commit -m "lesson-add(專案-chat-[專案名稱]): [一句話摘要]"
   git push
   ```

   **工具層（chat/cowork/code）**：
   ```
   git add claude-config/claude-chat.md   # 或對應檔案
   git commit -m "lesson-add(工具-chat): [一句話摘要]"
   git push
   ```

   **全域層**（同時更新兩處）：
   ```
   # 1. ~/.claude/CLAUDE.md（Web 雲端，直接寫入）
   # 2. WTF repo 同步：
   git add claude-config/CLAUDE.md
   git commit -m "lesson-add(全域): [一句話摘要]"
   git push
   ```

5. 回報：新增了什麼、刪除或合併了什麼、精簡前後行數變化。

## Chat Lesson 橋接

若使用者貼入格式為：
```
【Lesson 候選】
層級建議：...
內容：...
```
直接依層級建議執行，無需再詢問確認。
