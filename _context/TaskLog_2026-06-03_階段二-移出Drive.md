# 工作紀錄 2026-06-03 — 階段二：wtf-config 移出 Drive（前提反轉）

> 承接 `Handover_2026-06-03_階段二-wtf-config移出Drive.md`（已移 archive，其「案 C：抽 wtf-config 成獨立 repo」計畫被現實反轉而作廢）。

## 1. 前提反轉（關鍵）
接手敲決策點 D1–D5 時，用戶回答揭露：**已把整個 WTF repo 移出 Drive**（Windows `E:\Git_work\WTF_Under_Construction`，Mac `/Users/coma/Git_work/WTF_Under_Construction`）。檔案系統實況核對：cwd 已在 `E:\Git_work`、舊 Drive 副本 `E:\Claude_cowork\projects\WTF_Under_Construction` 已不存在。

→ `.git` lock 根因（雲端硬碟同步搶 `.git`）**已被整包移出根除**。原交接的「案 C：只抽 wtf-config 成獨立 repo」是「想把大專案留 Drive」的折衷，**變不必要**。決議：放棄 split、不建新 repo、不 submodule；wtf-config 留在 repo 內。

## 2. 用戶決策（取代 D1–D5）
- 架構：兩機整包移出 Drive、不 split。
- hook：只 `git pull`＋`sync`，**不 auto-commit**（commit 改手動，用戶說「更新全域設定/skills/規範」才 commit）、不清 lock。

## 3. Windows 已完成
### 3a. 階段二 repo（commit `b355f09`，已 push）
1. `wtf-config/projects-registry.md`：WTF 兩機 path → Git_work。
2. `wtf-config/sync_config.py`：`ROOT=SCRIPT_DIR.parents[2]` → `REPO_ROOT=SCRIPT_DIR.parent`；orphan 顯示 `dup.relative_to(ROOT)` → `str(dup)`（修 repo 搬離後 relative_to 對 Drive 專案拋 ValueError）；register workspace_root 改用 REPO_ROOT。
3. `~/.claude/wtf-sync.ps1`：`$WTF` → `E:\Git_work\WTF_Under_Construction`、刪「清 .git/*.lock」段。
4. SSOT 三檔（`AGENTS/CODEX/GEMINI.md`）來源註記去 Mac Drive 絕對路徑 → 機器中立。
5. 驗收：`sync`→`check` 全 7 OK（6 Drive 專案＋WTF repo 根）、~/.claude OK。

### 3b. skills 命名/規範對齊（commit `8010806`，已 push）
6. `session-end` SKILL：工作紀錄 `WorkLog_`→`TaskLog_`，補結案 `ClosedTaskLog_` 歸檔指引。
7. `wtf-config/audit_structure.py`：`CTX_PREFIXES`／日期檢查 `WorkLog_`→`TaskLog_`。
8. `session-start` SKILL：新增「讀取並套用 rules/ 規範」步驟（根＋專案，專案優先）；修 `_context/rules`→`rules` 路徑；完成回報改三步；**去掉每次補資料夾**（用戶指示不需每 session 做）。

### 3c. 跨機協調與 Mac 驗收
9. 建 Drive 協調區 `E:\Claude_cowork\projects\Git_work_agents\WTFrepo\`，釐清分工（repo 端 Windows owns、Mac 改本機 .sh＋驗收）。
10. Mac 驗收回報 **PASS、無分叉**：HEAD ff `b355f09`、registry Mac path 正確、`wtf-sync.sh` 已改（含 `exit 1→0` 補強）、`check` registry 11＋12 skills 全 OK。Mac 先前的平行重複編輯已 `git checkout -- .` 丟棄（即用戶說的「重複」，乾淨解決）。
11. **Drive 協調檔同步衝突修正**：`tail -F` 常駐鎖檔（Windows 專屬）擋 Drive 同步；改 **per-machine 單寫檔**（`signals_WIN.md`／`signals_MAC.md`）＋**輪詢式 monitor**（stat 比 mtime，不鎖檔）。
12. 知識：INDEX／lessons-learned／LESSONS 更新（含 Drive 協調、Windows 鎖檔專屬性兩條 lesson）。

## 4. 未完成／待 Mac
- Mac：`git pull` 取 `8010806`（skills）→ `sync`+`check` → 回報寫 `signals_MAC.md`。monitor `b60bhvme3` 盯回報。
- 整個 TaskLog 待 Mac 此項確認後可結案（改 `ClosedTaskLog_` 移 archive）。

## 5. 未處理（轉用戶）
- project `.claude/settings.json` 殘留死路徑（claude-config 舊名、Mac Drive 絕對路徑、Git_foler_anti）：agent 改 settings 被 auto-mode 擋，待用戶手動清。

## 6. 下一步
1. ~~session-end skill `WorkLog_`→`TaskLog_`~~ ✅ 完成（3b）。
2. ~~session-start skill 增 rules 套用步驟~~ ✅ 完成（3b）。
3. Mac pull `8010806`＋回報 → TaskLog 結案。
4. 執行專案工作（待用戶指派具體項目）。
5. （可選）清理 project `.claude/settings.json` 殘留死路徑（auto-mode 擋 agent 改，待用戶手動）。
