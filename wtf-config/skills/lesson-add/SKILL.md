---
name: lesson-add
description: 將觀察整合進對應層級的設定檔，去冗餘後存檔。用法：/lesson-add [層級] [內容]，或不帶參數自行觀察記錄。
---

# Lesson Add

用法：
- `/lesson-add [層級] [觀察內容]` — 指定內容
- `/lesson-add` 或 `/lesson-add 自行` — **自行觀察模式**：Agent 分析本 session，主動識別並記錄 lessons

## 自行觀察模式

不帶參數或帶「自行」呼叫時，執行以下流程：

**1. 回顧本 session：**
- 做了什麼修改、遇到什麼問題、如何解決
- 發現了什麼新行為、踩了什麼坑、確認了什麼假設

**2. 篩選值得記錄的觀察（嚴格篩選）：**

| 排除 | 原因 |
|------|------|
| 本 session 已直接更新過的設定檔 | 避免重複記錄 |
| 只適用本專案的實作細節 | 泛化價值低，放專案層 |
| 顯而易見的操作 | 不值得持久化 |
| 使用者已知的內容 | 浪費空間 |

**只記錄：** 可泛化到其他專案、非顯而易見、尚未在任何設定檔中出現的觀察。

**3. 判斷層級** → 依下方層級分析表決定。

**4. 執行** → 每條觀察各自 lesson-add，流程與手動模式相同。

**5. 報告** → 列出新增了什麼、排除了什麼（說明排除原因）。

層級：
- `專案` → 當前專案根目錄的 `.claude/CLAUDE.md`（Claude Code 專案）
- `專案 chat [專案名稱]` → `chat-project-lessons/[專案名稱].md`（Chat 專案知識庫）
- `全域` → `~/.claude/CLAUDE.md`（所有工具共用）+ `wtf-config/GLOBAL.md`（WTF repo 同步）
- `工具 chat rule` → `wtf-config/CLAUDE_CHAT.md` 的 `<!-- rules-start/end -->` **且同步更新** `dashboard.html` 的 `=== CHAT-TOOL-RULES-START/END ===`
- `工具 chat kb` → `wtf-config/CLAUDE_CHAT.md` 的 `<!-- kb-start/end -->`
- `工具 cowork` → `wtf-config/CLAUDE_COWORK.md`
- `工具 code` → `wtf-config/CLAUDE_CODE.md`
- `工具 gemini` → `wtf-config/GEMINI.md`
- `工具 codex` → `wtf-config/CODEX.md`

## 層級分析（自動判斷，可覆寫）

收到內容後先判斷適合層級：

| 若內容描述的是… | 建議層級 |
|---|---|
| Claude Code 專案的業務邏輯、檔案結構 | 專案 |
| Chat 專案的業務邏輯、操作慣例 | 專案 chat [專案名稱] |
| Chat 每次都要套用的行為規範 | 工具 chat rule |
| Chat 技術參考、環境限制、特定工具踩坑 | 工具 chat kb |
| Cowork 的 agent 行為、沙盒限制 | 工具 cowork |
| Claude Code 的檔案操作、git 流程 | 工具 code |
| Antigravity / Gemini 專屬設定與監控機制 | 工具 gemini |
| OpenAI Codex / Cursor 專屬設定與同步腳本 | 工具 codex |
| 跨工具都適用的溝通原則、思考框架、做到好底線 | 全域 |

若判斷層級與使用者指定不同，說明建議後詢問確認。

## 執行步驟

1. 依層級讀取對應檔案。

2. 將觀察整合進最相關的既有段落（不新增段落，除非真的無處安放）。

    **`工具 chat rule`**：
    - 寫入 `wtf-config/CLAUDE_CHAT.md` 的 `<!-- rules-start -->` 和 `<!-- rules-end -->` 之間。
    - **同步更新** `dashboard.html` 的 `=== CHAT-TOOL-RULES-START ===` 和 `=== CHAT-TOOL-RULES-END ===` 之間的陣列，在陣列末尾加入新項目。
    - 完成後提示：「⚠️ 固定規則已更新 — 請從儀表板重新複製 Project Instruction 貼回 claude.ai」

    **`工具 chat kb`**：
    - 寫入 `wtf-config/CLAUDE_CHAT.md` 的 `<!-- kb-start -->` 和 `<!-- kb-end -->` 之間。
    - 格式：`**[YYYY-MM-DD] 標題**\n內容。\n來源：[情境]。`
    - 完成後提示：「⚠️ 參考知識已更新 — 請重新上傳 CLAUDE_CHAT.md 至 Project Knowledge」

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

    **工具層 chat rule**（同時更新兩檔）：
    ```
    git add wtf-config/CLAUDE_CHAT.md dashboard.html
    git commit -m "lesson-add(工具-chat-rule): [一句話摘要]"
    git push
    ```

    **工具層 chat kb**：
    ```
    git add wtf-config/CLAUDE_CHAT.md
    git commit -m "lesson-add(工具-chat-kb): [一句話摘要]"
    git push
    ```

    **工具層（cowork/code/gemini/codex）**：
    ```
    git add wtf-config/[對應檔案]
    git commit -m "lesson-add(工具-[工具名]): [一句話摘要]"
    git push
    ```

    **全域層**（同時更新兩處）：
    ```
    # 1. ~/.claude/CLAUDE.md（本機，直接寫入）
    # 2. WTF repo 同步：
    git add wtf-config/GLOBAL.md
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

`rule` / `kb` 的判斷標準：
- **rule**：每次對話都應自動套用的行為規範（例：交接時機、開場流程）
- **kb**：有特定情境才有用的技術知識（例：環境限制、工具踩坑、API 行為）
