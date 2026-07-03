# 同 repo 多 CLI 並行（git worktree 隔離）
> 適用：同一 repo 有多個 Claude CLI／AI agent 同時工作時開啟；平時不載入
> 來源：原 CLAUDE_CODE.md 抽出（2026-07-03）；attendance-dashboard 2026-06-22 實戰彙整

- **各自建獨立 worktree＋分支**：每個 agent 各自 `git worktree add <dir> <branch>` 建獨立目錄與分支，working tree／index 完全隔離，互不踩 `git add`／不會吞掉彼此 staged 內容（解 index 全 repo 共用的撞車問題）。
- **共用紀錄檔各寫各的新檔**：TaskLog／lessons／INDEX 等共用文件改「各寫各的新檔」（依日期/主題/byline 區分），避免同檔 merge 衝突；確需共寫時最小插入＋帶 byline。
- **完工各自 merge main，後者先 pull**：各 worktree 完成後 merge 回 main；後 merge 的一方先 `git pull`／處理衝突再合，避免覆蓋先合者。

## Monitor 工具（並行監聽時）

- 監聽 log 檔用 `tail -n 0 -f` 而非 `tail -f`：`tail -f` 啟動時先顯示最後 10 行，log 被 append 就可能重播舊紀錄；`-n 0` 只看新增內容。
- 一個 session 啟動一次 persistent Monitor 即可，不需每個任務重新啟動。
