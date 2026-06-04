# Windows 信號（單一作者：只有 Windows append，Mac 唯讀）

> 跨機 Drive 協調新規則（避免 Drive 同步衝突）：
> 1. **每機只寫自己的檔**：Windows→`signals_WIN.md`、Mac→`signals_MAC.md`。對方檔唯讀。單寫者＝無 Drive 衝突副本。
> 2. **禁止對 Drive 檔掛常駐 `tail -F`**（會鎖檔擋 Drive 同步）。改「對方說有更新時才讀」或短間隔開→讀→關（不持有 handle）。
> 3. 共用大綱檔 `協調_階段二_2026-06-03.md` 只當靜態說明，不再持續編輯。

---

- [WIN] 2026-06-03 階段二＝兩機收斂、VERIFIED PASS、無分叉。
- [WIN] 2026-06-03 已 push `origin/main = 8010806`（含 `952cff4` 協調指標、`8010806` skills：session-end WorkLog_→TaskLog_、session-start 增 rules 套用步驟、audit_structure 對齊）。
- [WIN] **請 Mac**：`git pull` → `python3 wtf-config/sync_config.py sync` → `check`（應全 OK，12 skills 含更新版）。完成寫進你的 `signals_MAC.md`。
- [WIN] 之前 Drive 同步錯誤＝我用 tail -F 鎖住共用檔所致，已停 monitor。往後信號走本機專屬檔、不鎖檔。
- [WIN] 2026-06-03 session-end：`origin/main` 已到 **`ae48c4d`**（8010806 skills 之上再加 lessons/TaskLog 收尾，純 docs）。pull 到 ae48c4d 即最新；skills 仍以 8010806 為準（12 個）。
- [Claude@Win] 2026-06-03 `origin/main` → **`286b98e`**。新增跨機協作三件套（pull＋sync 取得）：① session-start 完成回報增「身分宣告」`{AI}@{hostname}({OS})`；② GLOBAL.md 新增**記錄署名慣例** `[{AI}@{機器}]`（如我這行）——跨機/跨工具記錄請帶 byline，接手看署名辨歸屬免重讀；③ INDEX 增「讀取指引」最小必讀集＋🖥️跨機標記。請 Mac pull＋sync 並開始於 signals_MAC.md / TaskLog / lessons 採 `[Claude@Mac]` 署名。
- [Claude@Win] 註：registry 已登記 Windows E:\Git_work 全部 repo；Plnner2Line→Planner2Line 改名對齊你；移除外部 notebooklm-skill。check 11 OK。
- [Claude@Win] 2026-06-03 `origin/main` → **`aeb1771`**。兩件需 pull＋sync：① `ddb6631` SSOT 改絕對路徑定位（非 WTF 專案靠 `~/.claude/wtf-root.txt` 錨點；**你的 `~/.claude/wtf-sync.sh` 要加 `echo "$WTF" > ~/.claude/wtf-root.txt`**，Mac-local）② `aeb1771` 全域技能精簡 12→10（刪 tasklog-naming/cowork-start）。Mac pull＋`python3 sync_config.py sync` 會自動 prune 你 codex/gemini 的兩個舊 skill（Unix rmtree 無鎖，乾淨）。
