# Lessons Learned (實戰教訓)

## 2026-06-03 (階段二：wtf-config 移出 Drive — 前提反轉)

* **整個 repo 移出雲端硬碟 ＞ 只 split 子目錄**：`.git` lock 的根因是雲端硬碟同步搶 `.git`。把**整個 WTF repo** 移出 Drive（兩機 Git_work）一步根除；原交接的「案 C：抽 wtf-config 成獨立 repo」是「想把大專案留 Drive、只讓 SSOT 逃出」的折衷，徒增兩 repo／submodule／跨機 clone 對齊成本。**用戶已先做了整包移出 → 前提變了，案 C 變不必要**。接手別照交接照單執行：先用檔案系統實況核對前提（本次 cwd 已在 `E:\Git_work`、Drive 副本已消失），前提變就重評方案。
* **SSOT 檔內禁寫單機絕對路徑**：`AGENTS/CODEX/GEMINI.md` 來源註記原寫死 Mac Drive 絕對路徑，跨機或搬遷即失準。多機共用的 SSOT 檔內路徑一律機器中立（指向 `projects-registry.md`），不放任一台的絕對路徑。
* **repo 搬離原階層 → `parents[N]`／`relative_to` 推導全崩**：`ROOT=SCRIPT_DIR.parents[2]` 假設 repo 在 `Claude_cowork/projects/WTF`；搬到 `Git_work` 後 parents[2] 變天，且 `dup.relative_to(ROOT)` 對仍在 Drive 的專案直接拋 ValueError（check 遇孤兒檔即崩）。凡靠相對層級推導的路徑，repo 一搬就壞；改用絕對 registry 路徑或 `SCRIPT_DIR.parent` 自身。
* **hook 不該 auto-commit**：用戶定調——register 改 machines.md 時間戳不該自動 commit；只有用戶明說「更新全域設定/skills/規範」才手動 commit。hook 收斂為純 `git pull`＋`sync`（讀取最新＋部署副本），不 push、不清 lock（repo 已離 Drive）。
* **Drive 跨機協調檔：單一作者 ＋ 不掛常駐 `tail -F`**：repo 移出 Drive 後改用 Drive 資料夾做即時跨機信號，踩兩坑：(1) 用 `tail -n 0 -F` 常駐 monitor 盯 Drive 檔，會**持有檔案 handle 鎖住檔案**，Drive 要用對方版覆蓋時被擋→「你的電腦不允許同步處理某些檔案」。(2) 單一共用檔被兩機輪流寫＝Drive 先天產生衝突副本。**正解**：每機只寫自己的檔（`signals_WIN.md`／`signals_MAC.md`，單寫者無衝突，對方唯讀）；Drive 檔**禁掛常駐 tail -F**，改輪詢式 monitor（每 ~20s `stat` 比 mtime/行數，有變才開檔一瞬即關，靠 sleep 釋放 handle），或 on-demand 讀。
* **「鎖檔擋同步」是 Windows 專屬，Mac 是另一種坑**：(1) 坑(1) Windows 檔案鎖強硬，handle 開著時 Drive 覆蓋/rename 被拒→報「不允許同步處理」；macOS/Unix 允許替換開啟中的檔（advisory lock），**不報此錯**（Mac 端未實測，依 Unix 語意推斷）。(2) 但 Mac `tail -f` 抓舊 inode，Drive 換檔後**靜默看不到新內容**（需 `tail -F` 按檔名重開）→ 不報錯卻漏訊。(3) 單一共用檔雙寫產生衝突副本＝**兩機都中**，與 OS 無關。故 per-machine 單寫檔＋輪詢不鎖檔對兩機皆有益。

## 2026-06-03 (階段一執行：跨機協作 + hook/git 實戰)

* **跨機 AI 協作＝共用檔案＋雙向 monitor**：兩端 AI（Win/Mac）在 Drive 同步的 markdown 交替 append、各自開 persistent Monitor 偵測對方標記（`[WIN-Rn]`/`[MAC-Rn]`、`DONE`/`VERIFIED` 信號），即可討論收斂＋分工執行＋互驗，免人工轉貼。**monitor pattern 兩個坑**：(1) grep 要限定 `[TAG-R數字]`，否則規則說明行裡的 `[MAC-Rn]` 範例會誤觸；(2) 基線 `prev` 要設為「啟動時的現有計數」，否則自己寫的信號會誤報成對方回覆。
* **Drive 同步的 `.git` 跨機不可靠 → 各機自己 add、單一端 commit**：staged index（`.git/index`）與 lock 跨 Drive 同步不可靠。跨機分工時檔案內容靠 Drive 一致即可，但 `git add`/`commit` 必須由一端在自己機器做，另一端 `git reset` 淨空 index 不重複 commit，否則歷史分叉。本次 Mac 改完→reset，TL(Windows) 自己 add+commit+push。
* **設定檔裡「自動執行的 hook」屬自我修改，classifier 會擋，需用戶明確授權**：agent 設計的 UserPromptSubmit hook（自動跑腳本、ExecutionPolicy Bypass）即使在分工 spec 內，寫入 `settings.json` 仍被 auto-mode classifier 擋下；要用戶在對話明確授權才放行。**破壞性或可疑操作（rmtree、跑被標記為有 bug 的舊版 sync）也會被擋——這是好護欄，別繞過**，改靜態驗收（讀碼確認）或請用戶授權。
* **UserPromptSubmit hook 一律 `exit 0`**：非零退出會阻擋使用者送出 prompt（Claude Code 行為）。Drive/git 偶發失敗不該擋使用者，hook 錯誤只印出、永遠 exit 0。Mac 版原 exit 1，Windows port 刻意改 exit 0。
* **註冊表＝單一部署清單**：`projects-registry.md`（專案×機器×絕對路徑）同時是「跨機路徑查表」與「sync/skills-install 的本機部署清單」，取代 `extra-scan-dirs.txt`＋相對路徑推導。新增專案／換機只改這一表，sync 取本機 hostname 的列即為部署目標。
* **git 追蹤的衍生副本會跨機 typechange**：root `AGENTS.md` 在 Mac 被 git 記為 symlink(mode 120000)、Windows 是實體檔 → 每次 pull 都 typechange、`M AGENTS.md` 永遠髒。解法：衍生副本一律 `.gitignore`＋`git rm --cached`（不入庫），由 sync 各機寫實體。

## 2026-06-03 (全域設定自動同步架構重整)

* **開場協議靠 hook，不靠 agent 自律**：CLAUDE.md 的「強制執行」依賴 agent 主動判斷，實踐中常跳過。唯一可靠方式：`settings.json` UserPromptSubmit hook 讓 harness 強制觸發，agent 無法繞過。hook 輸出透過 system-reminder 回報給 agent，agent 再向用戶確認。
* **Drive 路徑下 git pull 需先清 .lock**：Google Drive 同步 .git 會在 `refs/remotes/` 產生殘留 `.lock` 檔，導致 git pull 失敗。解法：pull 前 `find .git -name "*.lock" -delete`。已整合進 wtf-sync.sh。
* **機器專屬路徑的設定檔應放 repo，用 hostname:path 格式**：放在 `~/.claude/` 只有 Claude Code 能管理；放在 `wtf-config/extra-scan-dirs.txt` 加 `hostname:path` 格式，所有 agent 都能讀寫，各機器只套用自己那行。
* **AI 效能衰退的判斷與因應**：同一對話內發生事實歸因錯誤（把自己的提議誤記為用戶說的）屬能力衰退，不是正常波動。同一 model ID 不保證行為一致（可能靜默更新）。因應：降為執行層、關鍵狀態寫檔不依賴 AI 口述、開場協議改為用戶主動觸發、流程容錯優先。

## 2026-06-03 (skills 漂移整治與混合架構定案)

* **skills 採「混合架構」**：共用 skill（SSOT 11 個）只部署到全域 `~/.claude/skills/`（每台機器各一份實體副本，由 `sync_config.py sync` 維護），**不再複製進各專案 `.claude/skills/`**；專案層只放「專屬 skill」（如 data-verify、thumbnail-aware-images、remotion-best-practices）。理由：`sync_config.py` 從不同步專案層 skills，過去把共用 skill 複製進每個專案 → 各自過期成孤兒副本，是 skills 漂移的根因。
* **任何 skills/設定一律實體複製，禁止 symlink（再次踩雷確認）**：本次依舊版 `skills-install` skill 把專案 `.claude/skills` 改成 symlink，隨即發現違反既有鐵律——Drive/git 同步到 Windows 會變死檔。已全部還原為實體目錄。**過期的 skill/文件本身也會反過來誤導 agent**：修 SSOT 規則時，要連帶修「教學用的 skill 文件」（如 skills-install），否則下個 agent 照舊文又走錯。
* **Git_work（非 Drive 純 git 區）同樣適用無-symlink**：git 在 Mac 存實體目錄沒問題，但 Windows checkout 無權限時 symlink 會變文字檔。Git_work 各 repo 的共用 skill 已移除（靠全域），只留專屬。
* **zsh 不對未加引號變數做斷詞**：`for s in $VAR` 在 zsh（macOS 預設）不會把空白分隔的字串拆成多個詞，整串被當單一參數 → `rm -rf "$path/$VAR"` 靜默無效（有 -f 不報錯）。改用字面清單或陣列，或 `${=VAR}`。
* **`ai-team` 是共用 skill 的例外（範本＋就地實例）**：其 SKILL.md 規定專案文件（`AI_TEAM_DIVISION.md`/`AI_TEAM_WORKFLOW.md`/`agent-specs/*`）就地建在 `.claude/skills/ai-team/` 內。本次清理「共用副本」時整個刪掉 ai-team，連帶刪了 claude_CDIC_O4 的 7 支 Event agent-specs 與多專案填寫的 DIVISION/WORKFLOW（Git_work 已從 git 全數還原）。**教訓**：批次刪「共用 skill」前，先確認該 skill 資料夾內有無專案專屬巢狀檔；ai-team 這類「範本型」skill 在有客製的專案要整包保留。**Drive 區無 git，誤刪只能靠 Google Drive 網頁垃圾桶救**（約 30 天）——動 Drive 區檔案前更要先確認。
* **`sync_config.py` 全域部署用破壞性 rmtree，Windows 遇鎖定整批失敗**：`deploy_claude_dir()`（sync_config.py:174-181）對 `~/.claude/skills/` 做 `shutil.rmtree` 整批刪除再 `copytree`。Windows 上若任一 skill 資料夾被佔用（實測 ai-team 噴 `PermissionError WinError 5`，根因未驗證——推測編輯器/程序鎖定或防毒掃描），rmtree 中途失敗 → 全域 skills 整批沒部署（AGENTS.md 那段不受影響，照常寫 7 專案）。當下繞過法：單獨 `copytree` 目標 skill。**與 ai-team「絕不整包刪」是同一風險**：破壞性整批操作在 Drive／跨平台環境本就脆弱（同 symlink 失效、.git lock）。**修正方向（待施作）**：改逐 skill 就地覆蓋 `copytree(..., dirs_exist_ok=True)`，每 skill 包 try/except，單一鎖定只略過該項並回報，不毀全部；SSOT 已移除的舊 skill 再容錯刪除。此修正歸入 SSOT 同步架構討論的「階段一」（見 `workingfiles/SSOT同步架構討論_2026-06-03.md`）。

## 2026-06-02 (設定整合 T1/T6/T7 與結案規範)

* **寫新規則前先 grep 既有 skill/設定**：本次先在 GLOBAL.md 自訂「結案移 archive」與「WorkLog_」命名，事後才發現 `tasklog-naming` skill 早有「ClosedTaskLog_ 前綴」「TaskLog_」規範，造成兩處雙真相源衝突。新增任何規範前，先全域搜尋同主題是否已存在，否則必製造漂移。
* **「機械式」操作要驗證才算零歧義**：目錄改名 `output→outputs` 看似純機械，實則會打斷程式碼硬路徑引用（國圖南 `output/claude_layout/` 被 app.js/settings.json 引用）。凡涉及目錄改名/路徑，先 grep 引用再動，不可列入自動批次。
* **整理類腳本三段式安全**：report-only 稽核（`audit_structure.py`）→ dry-run 計畫（`organize_files.py` 預設）→ `--apply`。並把項目分 AUTO（機械零歧義，自動搬）/ MANUAL（成果vs素材等語意，只標記由人工拍板）。搬檔護欄：只搬不刪、同名不覆蓋、衝突跳過。
* **symlink 去中心化方案已被推翻**（修正 2026-05-24 lesson）：Drive 不支援跨平台 symlink，同步後變死檔。改為實體複製 + 同步腳本（`sync_config.py`）。任何新設計不再用 symlink。
* **Windows 主控台 cp950 中文亂碼**：Python 腳本輸出中文前加 `sys.stdout.reconfigure(encoding="utf-8")`，否則 print 出亂碼（檔案寫入用 utf-8 不受影響）。
* **交接待辦狀態用實況核對，別照單全收**：接手時前一份交接列「規則 commit 尚未執行」，實查 git log 發現交接後已有兩個 commit、working tree 乾淨＝該項已完成。交接文字是寫檔當下的快照，可能過時；接手第一步以 git/檔案實況驗證，不信任文件陳述（呼應 GLOBAL.md「關鍵狀態不依賴 AI 口述」）。

## 2026-05-24 (WTF 協作框架通用化與技能精簡)

* **去中心化與中立軟連結**：多 AI 代理協作時，將真實目錄命名為工具中立名稱（如 `_agents/skills`），並使代理預設目錄（如 `.claude/skills`）以軟連結（symlink）指向它，是實現去中心化與「唯一真理來源」的最優解。
* **溝通原則硬性限制**：在 `GLOBAL.md` 中寫入「禁止尊稱『您』」與「每次回應 300 字限制」，能有效約束 LLM 避免長篇大論、安撫討好與發散，顯著降低 token 開支。
* **開場提示一次性原則**：開場載入協議的「已載入設定」說明在同一個 session 中只需回報一次，後續問答應全面禁言該複本，直接進入對答。
* **技能共享與專案隔離混合架構**：為了避免專案獨有管理技能（如 `skills-prune`）混入全域同步目錄，專案層 `_agents/skills/` 應為實體資料夾，其中全域技能分別建立獨立 symlink，而專案獨有技能則直接以實體目錄隔離保存。
