# WorkLog — AI 效能衰退觀察與因應

**日期**：2026-05-24
**模型**：claude-sonnet-4-6

---

## 觀察到的問題

1. **開場協議未執行**
   CLAUDE.md 明定「每次對話開始時強制執行」，包含讀取 `about-me.md`、`lessons-learned.md`、專案 PRD。本次 session 完全跳過，直接回應使用者第一句話。

2. **同一對話內的事實歸因錯誤**
   AI 自己提議「設成 hook」，幾句話後誤記為「你之前說的」。這不是跨 session 記憶問題，是 context 完整存在時仍發生的追蹤失敗。以一年使用各種 AI 的經驗，屬前所未見。

3. **模型行為與兩週前相比明顯衰退**
   模型 ID 相同（`claude-sonnet-4-6`），但可靠性下降。推測原因：Anthropic 靜默更新 weights，同一 model ID 不保證行為一致。

---

## 根本分析

| 問題 | 原因 | 性質 |
|---|---|---|
| 開場協議跳過 | CLAUDE.md 是指令，不是程式觸發器；AI 自行判斷是否執行 | 行為不穩定 |
| 同對話歸因錯誤 | Context 追蹤失敗，非跨 session 問題 | 能力衰退 |
| 跨 session 一致性低 | LLM 輸出有隨機性；可能靜默更新 | 結構性限制 |

---

## 因應決策

1. **降低 Claude 在 ai-team 中的角色**：從 orchestrator 降為 execution tool。Tech Lead 由使用者擔任，或改用 Opus。
2. **開場協議改為使用者主動觸發**：對話開頭說「載入設定」，不依賴 AI 自動判斷。
3. **流程設計容錯優先**：任何 AI 犯錯時流程本身能接住，不以 AI 自主可靠性為前提。
4. **關鍵狀態寫入檔案**：不依賴 AI 口述追蹤「誰說了什麼」。

---

## 後續行動

- [x] 全域 lesson 已寫入 `claude-config/CLAUDE.md`（新增「AI 效能與可信度衰退因應」段落）
- [x] 修復 `~/.claude/CLAUDE.md` 斷裂的 symlink（2026-05-24，改指向 Google Drive 路徑）
- [x] 修復 `~/.claude/skills` 斷裂的 symlink（同上，`git_folder` 已整體移至 Google Drive）
- [x] 評估是否將 ai-team 框架中 Claude 的角色調整為執行層（2026-05-24 已完成「動態 Tech Lead」架構升級，Claude 可完全降為執行層，由使用者動態委派 Tech Lead 角色，並由指定的 Tech Lead 負責撰寫相關協作文件與 SPEC）
