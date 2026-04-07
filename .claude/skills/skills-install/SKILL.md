---
name: skills-install
description: 將 WTF repo 的 skills 安裝到目標專案。用法：/skills-install [目標專案路徑]
---

# Skills Install

將 WTF repo 的 `.claude/skills/` 複製到目標專案，讓該專案可使用所有共用 skills。

用法：`/skills-install [目標專案絕對路徑]`

執行步驟：

1. 確認來源與目標：
   ```
   來源：~/WTF_Under_Construction/.claude/skills/
   目標：[目標專案路徑]/.claude/skills/
   ```

2. 確認目標專案路徑存在，若 `.claude/` 不存在則建立：
   ```
   mkdir -p [目標專案路徑]/.claude/skills
   ```

3. 複製所有 skills（覆蓋舊版本）：
   ```
   cp -r ~/WTF_Under_Construction/.claude/skills/. [目標專案路徑]/.claude/skills/
   ```

4. 確認目標專案有 `.claude/CLAUDE.md`；若無，建立基本結構：
   ```markdown
   # [專案名稱] — 專案層級設定

   ## 專案概述
   [待補充]

   ## 專案特定規則
   [待補充]
   ```

5. 回報：已安裝哪些 skills、目標路徑、是否為首次安裝或覆蓋更新。

備註：
- 全域 skills 更新後，對所有已安裝的專案重跑一次即可同步。
- 不會覆蓋目標專案的 `.claude/CLAUDE.md`（專案設定各自獨立）。
