# 工作紀錄 2026-06-03 — 階段二：wtf-config 移出 Drive（前提反轉）

> 承接 `Handover_2026-06-03_階段二-wtf-config移出Drive.md`（已移 archive，其「案 C：抽 wtf-config 成獨立 repo」計畫被現實反轉而作廢）。

## 1. 前提反轉（關鍵）
接手敲決策點 D1–D5 時，用戶回答揭露：**已把整個 WTF repo 移出 Drive**（Windows `E:\Git_work\WTF_Under_Construction`，Mac `/Users/coma/Git_work/WTF_Under_Construction`）。檔案系統實況核對：cwd 已在 `E:\Git_work`、舊 Drive 副本 `E:\Claude_cowork\projects\WTF_Under_Construction` 已不存在。

→ `.git` lock 根因（雲端硬碟同步搶 `.git`）**已被整包移出根除**。原交接的「案 C：只抽 wtf-config 成獨立 repo」是「想把大專案留 Drive」的折衷，**變不必要**。決議：放棄 split、不建新 repo、不 submodule；wtf-config 留在 repo 內。

## 2. 用戶決策（取代 D1–D5）
- 架構：兩機整包移出 Drive、不 split。
- hook：只 `git pull`＋`sync`，**不 auto-commit**（commit 改手動，用戶說「更新全域設定/skills/規範」才 commit）、不清 lock。

## 3. Windows 已完成（本 commit）
1. `wtf-config/projects-registry.md`：WTF 兩機 path → Git_work（Mac 列代填待 Mac 核對）。
2. `wtf-config/sync_config.py`：`ROOT=SCRIPT_DIR.parents[2]` → `REPO_ROOT=SCRIPT_DIR.parent`；orphan 顯示 `dup.relative_to(ROOT)` → `str(dup)`（修 repo 搬離後 relative_to 對 Drive 專案拋 ValueError）；register workspace_root 改用 REPO_ROOT。
3. `~/.claude/wtf-sync.ps1`：`$WTF` → `E:\Git_work\WTF_Under_Construction`、刪「清 .git/*.lock」段。
4. SSOT 三檔（`AGENTS/CODEX/GEMINI.md`）來源註記去 Mac Drive 絕對路徑 → 機器中立（指向 registry）。
5. 知識：INDEX／lessons-learned／LESSONS 更新。
6. 驗收：`sync`→`check` 全 7 OK（6 Drive 專案＋WTF repo 根）、~/.claude OK、無崩潰。

## 4. 未完成／待 Mac（見 workingfiles/階段二執行_2026-06-03.md 信號區）
- Mac：`git pull` → 核對 registry Mac WTF path → 改 `~/.claude/wtf-sync.sh`（路徑、刪清 lock、不加 auto-commit）→ `sync`+`check` 驗 11 列 OK → 回報。

## 5. 未處理（轉用戶）
- project `.claude/settings.json` 殘留死路徑（claude-config 舊名、Mac Drive 絕對路徑、Git_foler_anti）：agent 改 settings 被 auto-mode 擋，待用戶手動清。

## 6. 下一步
1. session-end 相關 skill：`WorkLog_` 命名 → `TaskLog_`，依 rules 修正。
2. session-start skill 增一項（依 rules 資料夾內容）。
3. 執行專案工作（待用戶指派）。
