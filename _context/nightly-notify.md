# 全域設定修改建議（nightly → 用戶核准）

> 夜間 routine **不可自行修改全域設定**（GLOBAL.md／wtf-config SSOT），只能在此 append `- [ ]` **建議**。
> 本機 session-start 開場讀此檔，有未勾項即醒目提醒：「nightly 建議改全域設定：X，要採用嗎？」
> 用戶核准 → 自行套用該建議並移除/勾掉該行；不採用 → 直接刪該行。（lessons 加性更新不在此，routine 可自動加）
> 機制：routine 寫建議 → commit main → 本機 hook pull → session-start 浮出。

---
- [x] 2026-07-03 Fable5 session 建議修改全域設定（Mac 已套用：SessionStart hook + wtf-sync 顯性化失敗）
  - `~/.claude/settings.json`（各機本地）：hooks 加 SessionStart 注入三檔制提醒（實測新 session 不會自動照 CLAUDE.md 跑開場協議；語法查證自 https://code.claude.com/docs/en/hooks.md）：`"SessionStart": [{"hooks": [{"type": "command", "command": "echo '【開場協議-hook注入】專案知識三檔制:1) _context/INDEX.md 2) INDEX指到的當前TaskLog 3) _context/lessons-learned.md;嚴禁全量掃_context/;動手前過GLOBAL.md制度層派工鐵律。'"}]}]`（不加 matcher＝startup/resume/compact 都注入，壓縮後也會重新錨定）
  - `~/.claude/` 的 wtf-sync 腳本（各機本地）：git pull 失敗時 echo「⚠️ wtf-sync 失敗:<原因>」再退出（stdout 會注入 context），禁止靜默 exit 0——Windows 實測已因本機未 commit 變更悄悄失敗多次。
