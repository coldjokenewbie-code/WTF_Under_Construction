# Chat Project Lessons

各專案在 Claude Chat 累積的知識與經驗。

## 結構

每個專案一個檔案：`[專案名稱].md`

例：
- `MS-Office-自動化流程.md`
- `Planner2Line.md`

## 使用方式

1. **Chat 讀取**：在 Project Instruction 加入對應檔案的 GitHub raw URL
2. **寫入**：說「整理 lesson」→ Chat 輸出候選 → Claude Code 執行 `/lesson-add 專案 [專案名稱] [內容]`
3. **格式**：見各檔案內的 `<!-- lessons-start/end -->` 區塊

## Lesson 層級決策

- 只跟此專案有關 → 此資料夾
- Chat 工具通用慣例 → `claude-config/claude-chat.md`
- 所有工具都適用 → `claude-config/CLAUDE.md`
