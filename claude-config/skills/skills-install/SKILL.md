---
name: skills-install
description: 將 WTF repo 的 skills 同步到全域環境或目標專案。用法：/skills-install [--global] | [目標專案路徑]
---

# Skills Install

將 WTF repo 的 `claude-config/skills/` 複製到全域環境或目標專案，確保工具鏈同步。

用法：
- `/skills-install` 或 `/skills-install --global`: 同步至 Claude 與 Antigravity 全域環境。
- `/skills-install [目標專案絕對路徑]`: 同步至特定專案目錄。

執行步驟：

1. 確認模式與目標：
   - **全域模式**（無參數或 `--global`）：
     - Claude 全域：`~/.claude/skills/`
     - Antigravity 全域：`~/.gemini/antigravity/global_skills/`
   - **專案模式**（提供路徑）：
     - 目標：`[路徑]/.claude/skills/`

2. 確認目的地存在：
   - 全域目錄通常已存在，若不存在則建立。
   - 專案模式下，若 `[路徑]/.claude/` 不存在則建立。

3. 執行複製（覆蓋舊版本）：
   - 來源：`~/WTF_Under_Construction/claude-config/skills/`
   - 使用 `cp -r` 或 `xcopy` 將所有 skill 子目錄同步至目的地。


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
