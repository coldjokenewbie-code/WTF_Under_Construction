# 全域設定修改建議（nightly → 用戶核准）

> 夜間 routine **不可自行修改全域設定**（GLOBAL.md／wtf-config SSOT），只能在此 append `- [ ]` **建議**。
> 本機 session-start 開場讀此檔，有未勾項即醒目提醒：「nightly 建議改全域設定：X，要採用嗎？」
> 用戶核准 → 自行套用該建議並移除/勾掉該行；不採用 → 直接刪該行。（lessons 加性更新不在此，routine 可自動加）
> 機制：routine 寫建議 → commit main → 本機 hook pull → session-start 浮出。

---

- [ ] 2026-06-23 nightly 建議修改全域設定（待用戶核准）
  - `wtf-config/CLAUDE_CODE.md`：新增「同 repo 多個 Claude CLI 並行工作，應各自 `git worktree add <dir> <branch>` 建獨立目錄＋分支，working tree/index 完全隔離不互踩 `git add`；共用紀錄檔（TaskLog/lessons/INDEX）改「各寫各的新檔」避免 merge 衝突；各自完工後 merge main（後者先 pull）」—— 來源：attendance-dashboard 2026-06-22 實戰彙整
