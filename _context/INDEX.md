# WTF_Under_Construction — 現況總覽 (INDEX)
> 進場先讀。最後更新：2026-06-03

## 一句話目標
Workflows That Flow：以複利方式累積 Claude 協作效率與效益。設定、Skills、流程皆為可累積資產，不做一次性修補。本專案即跨工具（Claude Code / Cowork / Codex / Antigravity）設定與 Skills 的真相源（SSOT）。

## 目前狀態 / 進度
- SSOT 設定已就緒：`wtf-config/`（GLOBAL.md、AGENTS.md、LESSONS.md、machines.md、sync_config.py、audit_structure.py、organize_files.py、skills/）。
- 設定檢查 7/7 AGENTS.md 一致；working tree 乾淨（HEAD `5b98a90`，截至 2026-06-02 交接）。
- Mac 現況：`~/.claude/CLAUDE_CODE.md` 與 `~/.claude/skills` 仍為指向 `wtf-config/` 的 symlink。
- `sync_config.py` 範圍僅 `projects/*/AGENTS.md`，不處理 `~/.claude/`。

## 關鍵檔案
- 最新交接：`_context/Handover_2026-06-02_設定載入與交接狀態核對.md`
- 最新工作紀錄：`_context/TaskLog_2026-06-02_設定載入與交接狀態核對.md`
- SSOT：`wtf-config/GLOBAL.md`、`wtf-config/AGENTS.md`
- lessons：`_context/lessons-learned.md`、雲端層 `wtf-config/LESSONS.md`
- archive：`_context/archive/`（已結案交接）

## 待辦 / 下一步
1. ✅ **T5**：孤兒 `AGENTS (1).md` 本次盤點未發現（已清/僅存他機）。
2. ✅ 各專案建 `_context/INDEX.md`（Drive 8 個 + Git_work 4 個，2026-06-03 完成）。
3. ✅ **T2 skills 漂移**（2026-06-03 完成）：handover `WorkLog_→TaskLog_`、skills-install 改實體複製、確立**混合架構**（共用走全域、專案只留專屬）、移除各專案共用副本與 symlink 殘留、清 Git_work `._agents` 殘渣。詳見 lessons-learned 2026-06-03。
4. **T6/T7 收尾**：26 項 MANUAL 搬檔（`output/`→`outputs/` 改名前先 grep 引用）、lessons 逐專案彙整進 `wtf-config/LESSONS.md`。
5. repo 移出 Drive 後續：lesson「Drive 同步 .git 會損壞 repo」寫進 GLOBAL.md、修 lesson-add skill 路徑、notebooklm-skill remote 決策、跨機部署。
6. **P2**：修 `sync_config.py` 編碼（Windows cp950 `✓` UnicodeEncodeError）。

## Git_work 區提醒（需在實機 commit）
- Git_work 4 repo 的 skills 清理與新增 `_context/INDEX.md` 皆為 working tree 變更，待使用者在各 repo 自行 commit。
- `claude_CDIC_O4` 有 P0 待辦：`git reset --hard origin/main` + `git stash pop`（見其 INDEX）。

## 備註
- 待確認（Windows）：`~/.claude/CLAUDE.md` 是否存在且為 WTF 設定；若無需決定擴充 sync_config.py 覆蓋 `~/.claude/` 或手動複製。
- `sync_config.py check` 在 Windows（cp950）會因 `✓` UnicodeEncodeError 中斷；執行前須 `$env:PYTHONIOENCODING="utf-8"`。
