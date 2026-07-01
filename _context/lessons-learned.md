# Lessons Learned (實戰教訓)

## 2026-07-02 (AI 助理框架 / 視覺評分嚴格 / 待辦整合)

* **視覺品質評分要嚴格，「盲評」系統性灌水**：讓看不到畫面的 headless agent（Codex/Antigravity）用「文字描述」打視覺分，它只會照被美化的描述給高分——實測描述完 blueprint 版給 7.4→8.1，PO 看真畫面說「非常糟、1-2 分」。視覺真相源＝**實際截圖**（我 `Read` PNG 親眼看）＋PO 目視；agent 只能協助 rubric/挑毛病，不能當分數來源。CSS+emoji／無真實影像／無留白＝學生作品；一流 museum app＝一張強主視覺(滿版真圖)＋極簡字＋大留白＋單一動作，**克制 > 堆裝飾**。要真實影像才可能及格（授權後抓免費 PD 圖/生成並標來源）。
* **「AI 助理框架」＝治 agent 的 harness，不是工作流函式庫**：預先註冊每個 handler ＝使用者得先定義每個流程＝跟直接下指令沒差、無槓桿。使用者要的是**對任意任務都強制紀律**：動工前立契約(範疇+驗收標準+授權 preflight)、宣稱完成前必附自驗證據才放行、每次留紀錄定期回顧。關鍵「靠結構強制、不靠 AI 自律」（**溝通冗贅＝紀律漂移徵兆**）。跨工具 hook 不對等(只 Claude Code 有原生攔截 hook)→強制點放外部＋**教練/品管制(換另一個 AI 驗收，結構杜絕自驗自過)**。
* **本地優先路由省 API；自訂 delimiter 會撞 Policy Gate**：確定性 handler 命中 registry 即繞過 LLM（llm_calls=0）。實作踩坑：git `--format=%h|%ad|%s` 的 `|` 被 Policy Gate 當 shell 元字元/注入擋下（**反證 policy 有效**）→ 改 ASCII unit separator `%x1f`。安全閘經驗收又補：禁執行寫入區(data/outputs)腳本(write-then-execute)、git 網路子命令(clone/pull/fetch)在 allow_network=false 時拒、realpath 反 symlink 改名。
* **待辦架構定案：TaskLog=真相源、待辦 App=鏡像、廢 INBOX.md**：語音(Obsidian Inbox)→ `/inbox` 分流：專案工作→該專案 TaskLog(真相源)＋鏡像進 ai-team-todo App(owner=AI)；個人雜務(報帳/租車)→只進 App(owner=user)。App owner 分 user/AI 讓 PO 掌握「AI 執行工作量」。廢 INBOX 避免 INBOX/INDEX/TaskLog 三頭馬車。**/inbox 收尾只 `git add` 本次寫入的 TaskLog 檔**，勿 `add _context/`／`-A`（會掃進無關未追蹤檔，本次誤committed 一個舊 TaskLog）。

## 2026-07-02b (ody 小隊：紀律靠 hook 強制、hook 不熱載、跨工具開場載入)

* **紀律要「輸出守門」機器攔截，不靠自律；錯誤轉可機檢規則才有複利**：Claude 一再違反「極簡/禁聊天語氣」需重複提醒＝規範停 prompt 層、無輸出檢查。解＝ody 守門：`tools/ody/squad/reply_lint.py`(禁詞+字數) + `stop_hook.py`(Stop hook，命中禁詞 block 重寫，防迴圈+fail-open)。學習＝每次糾正把樣式加進 `lint_rules.json`（Mentor 維護），下次自動擋——**加規則不寫心得**才複利。
* **Claude Code hook 不熱載，需重啟 session**（claude-code-guide 查證：issue #22679 快取、#53538 熱載未實作；`/hooks` 只顯示不重載）。→ 改 settings.local.json 加 hook 後**本對話不生效，下個新 session 才載**。驗 hook 要開新對話。
* **跨工具紀律強制（Codex/Antigravity 無原生 Stop hook）**：規則寫進各自全域開場必讀檔（`wtf-config/CODEX.md`→`~/.codex/AGENTS.md`、`GEMINI.md`→`~/.gemini/GEMINI.md`；非 skill lazy-load）＋**輸出前自跑 `reply_lint.py` 自檢**（草稿→lint→改稿→過關才輸出）。三工具共用同一 lint 規則庫＝全域一致守門。
* **框架命名要對得上能力**：`tools/assistant/` 只做註冊過的 handler、非通用助理 → 使用者要求改名，改 `tools/ody/`（奧德賽小隊基礎設施）。名不符實會誤導期待。

## 2026-06-07 (/inbox 首次實跑：快速捕捉工具不中途問、標題式為常態、重複不重收)

* **快速捕捉型指令（/inbox）下了就一路處理完，禁中途用 AskUserQuestion 問**：用戶用 `/inbox` 是為了「快速紀錄想法/待辦」，回覆問題的時間他自己早分流完了——要他標注他不如自己做。歸屬有多候選（如 `claude_CDIC_O4` vs `cowork_CDIC`）時，**自行依關鍵詞/近期活躍度歸納**，判不出才落 WTF `_context/INBOX.md`「未分類」；不要停下問。判斷一個指令是否「可中途問」：它的價值是否來自「省用戶時間」，是則零打斷。
* **標題式速記（正文空）是多數常態，不是異常**：手機語音快速紀錄多半只有標題、無內文。不要把「正文為空」當問題回報或要用戶補；標題本身就是內容，照常分流。
* **重複速記不重收**：同名/同內容且先前已收錄者（本例 Drive 回寫使「工作修正出勤專案的儀表板」二度出現），**不再寫入 INBOX，只把原檔移出 Clippings 到 Ingested 清掉**，避免 INBOX 長出重複條目。
* **skill 源與用戶當場定調衝突要回頭修源**：原 `wtf-config/skills/inbox/SKILL.md` 第 2 步寫「判定有疑慮先列給用戶確認」，正是它誘導我去問而被糾正。當場校準後應回修 skill 源並 `sync` 重新部署，否則下次照舊文又走錯（呼應「過期文件會反過來誤導 agent」）。

## 2026-06-17 (session-start python 指令依平台選擇)

* **`session-start` hook 呼叫 python 需依平台選指令**：環境 block 已含 `Platform` 欄位（`mac`/`linux`=`python3`，`windows`=`python`）。若寫死 `python` 在 Mac/Linux 回 `command not found`；寫死 `python3` 在 Windows 可能失敗。正確做法：讀 Platform → 選 `<PY>` → 代入指令，免試錯。此規則適用所有在 session-start 跑的 shell 腳本。

## 2026-06-09 (判讀／指派工作紀律：禁無證據硬湊、先建驗證視圖再判定)

* **無證據絕不硬湊一個值**：配對/指派時若某項找不到依據，正確做法是標「未知」交人工審核，**禁止「找個附近沒用到的選項」填上去**。實例：PPT 拉線標註把 `2B-1` 錯讓出正確的 `td21` 後，因無引線依據，竟隨手挑一個附近沒用到的 `td224` 填給 `2B-1`——等於製造一筆假資料。寧可空、寧可標問號，不可憑空捏。
* **先建立可靠的驗證視圖，再做判定（時序紀律）**：在缺乏可靠辨識工具時用肉眼瞎猜＝高錯誤率。應**先**把資料轉成高對比/可追蹤的檢視（本例：參考頁引線染紅＋底圖加半透明綠遮罩＋每定位點標 ID），**再**做指派。本例此招還是使用者提醒才用，順序顛倒導致先猜錯。任何「靠看圖判斷」的任務，先問：我有沒有先把它變得好判讀？
* **鄰近 ≠ 連線；高信心數據不得被肉眼印象推翻**：元素「離哪個標的近」不等於「它連到哪個標的」（標籤密集、引線交叉時尤其）。唯一真相是那條連接線。當程式/幾何已給出近乎精確的配對（端點距離≈0），**不得用模糊的空間鄰近印象去推翻**它——本例正是用「pin 看起來在另一標籤旁」推翻了 d≈0 的鐵證，鑄成錯誤。判定優先序：可追蹤的連接證據 > 高信心幾何 > 肉眼鄰近（最低）。

## 2026-06-08 (互動 HTML 產出物自驗：全域 playwright + file:// 中文檔名)

* **互動 HTML 交付前用 playwright 自驗、不靠肉眼**：產出帶 JS 互動（tab 切換、判斷器、複製鈕）的 HTML，落地前跑 headless 煙霧測試——掛 `pageerror`／`console error` listener 抓 JS 錯，再 `click` 幾個互動點斷言 class/文字變化（如判斷器走指定分支驗結論）。比只截一張圖更能抓到「畫面對但互動壞」。截圖驗完即刪（放 `workingfiles/_screenshots/`）。
* **專案沒裝 playwright 時走全域絕對路徑 require**：本機 playwright 是 `npm -g`（`~/AppData/Roaming/npm/node_modules/playwright`），專案 `node_modules` 沒有 → `require('playwright')` 失敗；改 `require('C:/.../npm/node_modules/playwright')` 絕對路徑即可，不必在專案 `npm i`。chromium 已在 `~/AppData/Local/ms-playwright`。
* **`file://` 開中文檔名要先 URL-encode**：`file:///E:/.../ai-team-協作說明.html` 直接丟 `page.goto` 在 Windows 會找不到；中文片段需 `encodeURIComponent`（空格→`%20`、中文→百分比碼）才載得到。

## 2026-06-08 (ai-team cli-reference 分段 + sync gap + agent 規格禁推測)

* **ai-team cli-reference 應按角色分段，各 agent 只讀自己那段**：多 agent 共用的技術文件改為三段（Codex TL / Antigravity TL / Claude TL），共用概念獨立一節；每個 agent 進場只讀自己的段落，降低 context 耗費與認知負載。同樣原則適用任何 multi-agent 操作手冊。
* **`sync_config.py deploy_other_tools()` 只清 symlink、不清實體舊檔**：換機或工具重裝後，`~/.gemini/AGENTS.md` 等實體舊檔以 stale 版本殘留，`deploy` 不會覆蓋；需手動清除後再跑 sync（已知 gap，待修 `deploy_other_tools` 邏輯，改為：同名實體舊檔先 `unlink` 再複製）。
* **禁止推測填入未實測的 agent CLI 規格**：另一 agent 的行為規格（指令格式、寫檔限制、信號慣例）必須由**當事 agent 實測或自報後再落檔**，不得由他方推測補充（推測結果會把自己的行為當成對方的）。呼應「誠實告知」但在 ai-team 中需明訂。

## 2026-06-08 (Nightly routine 雲端跨 repo 掃描：靠 trigger 預掛載，不能 clone)

* **雲端 routine 掃多 repo 只能靠 trigger 預掛載，不能 `git clone`**：雲端 ephemeral container 直連 github.com 無憑證（git 認證走 local proxy、無 `GITHUB_TOKEN`），`git clone https://github.com/...` 必失敗（實測 `could not read Username`）。可掃的 repo＝已在 trigger「Repositories」欄掛載、由環境**預先 clone 到 `/home/user/<repo>`** 的那些；對它們只能 `git -C pull/log`。v2.0 一度把 v1.0 的「靠預掛載」改成「從 registry 動態 clone」，反而比 v1.0 掃得更少（clone 全失敗、只剩 WTF 自己）——**動態 clone 是對雲端無效的死碼，真正開關是 trigger 掛載清單**。registry 增刪 repo 後必須回 trigger UI（CLI `/schedule update` 對話式可改 repo、無 flag 式批次）同步重掛，否則靜默漏掉。
* **「實證能跑」要先釐清靠的是哪個機制再下結論**：v1.0 能掃他 repo 不是因為 clone 成功，而是它**從不 clone**、直接讀 trigger 預掛載的目錄。只看 prompt 文字會把「致命」歸錯因；對照 trigger 設定（掛載 repo 清單）＋實測 clone 才看清真正機制。
* **雲端 routine 時區用 `TZ='Asia/Taipei'` 定義「今日」**：container 預設 UTC，`date +%Y-%m-%d` 與 `git log --since` 會把台灣晚間（UTC+8）的 commit 切到不同 UTC 日 → 漏抓/誤抓。掃描與 commit 步驟前 `export TZ='Asia/Taipei'`、`git log` 加 `--date=local`。
* **`git log --oneline` 與 `--format` 並用，前者被覆蓋**：`--oneline`=`--pretty=oneline --abbrev-commit`，後接 `--format` 會勝出使 `--oneline` 失效（不報錯、語意混亂）。要自訂格式就只留 `--format`。

## 2026-06-07 (跨工具開場載入對等：per-machine 部署洞 + 各工具原生檔名)

* **每個工具認自己的原生檔名，別憑同名假設**：Codex 原生開場讀 `~/.codex/AGENTS.md`，**不讀 `~/.codex/CODEX.md`**（用 `codex debug prompt-input` 實測注入內容確認）；Antigravity 讀 `~/.gemini/GEMINI.md`。WTF 早期把 SSOT 用「同名 symlink」掛上去（CODEX.md／GEMINI.md），既非工具原生入口、又因 repo 移出 Drive 而 dangling，導致 codex/gemini 開場一個月沒載入任何全域設定。**部署到工具原生會讀的檔名，並用實體副本（symlink 跨平台/搬遷必斷）**。跨工具設定前，先問該工具「你開場實際讀哪個檔」（headless 可實證），不要照 Claude 的習慣套。
* **per-machine 部署是無聲洞，要主動驗 + 寫對機待辦**：`deploy_other_tools()` 只部署 skills，漏了全域指令檔，且 `check` 從不驗 ~/.codex、~/.gemini → 斷鏈無告警。修法：`check` 把「工具原生指令檔存在且非空」納入掃描（斷鏈/空檔即報 BROKEN/MISSING）。本機修好 ≠ 另一台修好；每次這類部署收尾必寫 Windows 待辦（見記憶 cross-system-sync-always）。
* **三工具都有 headless CLI → ai-team 同機改 CLI 直驅**：`claude -p`／`codex exec`／`agy --print` 可同步互叫。同機協作不再需 `AGENT_SIGNAL.log`＋MONITOR 中繼（那是為無 CLI 的 GUI agent 設計）；信號檔降為跨機/GUI/持久化 fallback。headless 皆單次無狀態，多輪由 lead 每輪餵脈絡；卡住要追原因重跑、不跳過。

## 2026-06-07 (技能載入：原生 lazy-load 已涵蓋，勿開場強制讀全部)

* **別重複工具原生已做的事**：GLOBAL/AGENTS 原規定「開場 `view_file` 讀取所有啟用中 SKILL.md body、禁止僅口頭宣示」。但 Claude Code 原生已把每個 skill 的**名稱＋描述**自動列在可用清單，body 只在 `Skill` 觸發時才需讀。開場強讀全部 body＝每個 session 付一次冤枉 token，且隨 skill 增多線性惡化。**改**：開場只認自動清單＋簡述相關 skill，觸發才讀 body。寫「強制載入」類規則前先確認工具是否已原生提供，否則是疊床架屋。
* **「數量門檻」常是錯的代理指標**：原「全域 skill >10 即提示精簡」是在補「開場讀全部」的成本洞；一旦 body 不在開場載入，**數量不再有 context 成本**，門檻失去意義。廢除數量門檻，改以「功能重疊／描述含混」為精簡準則——治本（移除成本來源）後，治標的閾值就該一併撤除，否則留著製造假警報。

## 2026-06-04 (跨工具 skill 部署：dangling symlink 盲點)

* **舊架構死 symlink 會被誤當「工具自有」保留，擋住實體覆蓋**：Mac `~/.codex/skills/` 殘留 5 月舊 symlink 架構的連結，指向已不存在的 `/Users/coma/git_folder/.../claude-config/skills/`（`git_folder`→今 `Git_work`、`claude-config`→今 `wtf-config`）。`deploy_other_tools()` 的 `copytree(dirs_exist_ok=True)` 對 symlink 拋 `FileExistsError(Errno 17)` 而略過 → codex 讀到斷鏈、skill 從沒被更新（gemini 是實體目錄故正常，差異即線索）。`sync` 報「寫入 1 個」而非 10 個就是徵兆。原設計「symlink＝工具自有（find-skills）要保護」假設**沒涵蓋死連結**。**修**：複製前 `if dst.is_symlink(): dst.unlink()`——只拆與 SSOT **同名**的 symlink（find-skills 等不同名不受影響），再 copytree 寫實體。換機/復原免再手動清。已注入 dangling symlink 實測自動修復通過。
* **同步報表的數字要核**：`sync` 印「寫入 N 個 skill」，N 與預期（10）不符就是部署沒全成；別只看末行 `v 寫入` 就當完成。

## 2026-06-03 (階段二：wtf-config 移出 Drive — 前提反轉)

* **整個 repo 移出雲端硬碟 ＞ 只 split 子目錄**：`.git` lock 的根因是雲端硬碟同步搶 `.git`。把**整個 WTF repo** 移出 Drive（兩機 Git_work）一步根除；原交接的「案 C：抽 wtf-config 成獨立 repo」是「想把大專案留 Drive、只讓 SSOT 逃出」的折衷，徒增兩 repo／submodule／跨機 clone 對齊成本。**用戶已先做了整包移出 → 前提變了，案 C 變不必要**。接手別照交接照單執行：先用檔案系統實況核對前提（本次 cwd 已在 `E:\Git_work`、Drive 副本已消失），前提變就重評方案。
* **SSOT 檔內禁寫單機絕對路徑**：`AGENTS/CODEX/GEMINI.md` 來源註記原寫死 Mac Drive 絕對路徑，跨機或搬遷即失準。多機共用的 SSOT 檔內路徑一律機器中立（指向 `projects-registry.md`），不放任一台的絕對路徑。
* **repo 搬離原階層 → `parents[N]`／`relative_to` 推導全崩**：`ROOT=SCRIPT_DIR.parents[2]` 假設 repo 在 `Claude_cowork/projects/WTF`；搬到 `Git_work` 後 parents[2] 變天，且 `dup.relative_to(ROOT)` 對仍在 Drive 的專案直接拋 ValueError（check 遇孤兒檔即崩）。凡靠相對層級推導的路徑，repo 一搬就壞；改用絕對 registry 路徑或 `SCRIPT_DIR.parent` 自身。
* **hook 不該 auto-commit**：用戶定調——register 改 machines.md 時間戳不該自動 commit；只有用戶明說「更新全域設定/skills/規範」才手動 commit。hook 收斂為純 `git pull`＋`sync`（讀取最新＋部署副本），不 push、不清 lock（repo 已離 Drive）。
* **Drive 跨機協調檔：單一作者 ＋ 不掛常駐 `tail -F`**：repo 移出 Drive 後改用 Drive 資料夾做即時跨機信號，踩兩坑：(1) 用 `tail -n 0 -F` 常駐 monitor 盯 Drive 檔，會**持有檔案 handle 鎖住檔案**，Drive 要用對方版覆蓋時被擋→「你的電腦不允許同步處理某些檔案」。(2) 單一共用檔被兩機輪流寫＝Drive 先天產生衝突副本。**正解**：每機只寫自己的檔（`signals_WIN.md`／`signals_MAC.md`，單寫者無衝突，對方唯讀）；Drive 檔**禁掛常駐 tail -F**，改輪詢式 monitor（每 ~20s `stat` 比 mtime/行數，有變才開檔一瞬即關，靠 sleep 釋放 handle），或 on-demand 讀。
* **「鎖檔擋同步」是 Windows 專屬，Mac 是另一種坑**：(1) 坑(1) Windows 檔案鎖強硬，handle 開著時 Drive 覆蓋/rename 被拒→報「不允許同步處理」；macOS/Unix 允許替換開啟中的檔（advisory lock），**不報此錯**（Mac 端未實測，依 Unix 語意推斷）。(2) 但 Mac `tail -f` 抓舊 inode，Drive 換檔後**靜默看不到新內容**（需 `tail -F` 按檔名重開）→ 不報錯卻漏訊。(3) 單一共用檔雙寫產生衝突副本＝**兩機都中**，與 OS 無關。故 per-machine 單寫檔＋輪詢不鎖檔對兩機皆有益。

## 2026-06-04 (夜間 routine 評估與 realign)

* **雲端 routine commit 到死分支＝自動更新沒生效**：nightly 排程每晚 commit 到 `claude/nightly-*`／`kind-knuth-*` 分支、**從不併 main**，故它的 lesson-add／GLOBAL 精簡全卡在死分支，真 SSOT 從沒拿到。用戶以為「自動學習」有在跑，實際 main 上的 lessons 都是本機工作時 lesson-add 進去的。**要讓排程的自動更新生效，必須 `git pull --rebase origin main`→改→`push origin main`（衝突即 abort 不硬推），不要推到永不 merge 的分支。**
* **雲端 ephemeral container 看不到本機 transcript**：排程跑在雲端、工作 session 在本機 → 「分析 transcript 自動學 lesson」結構性失效（log 自己反覆寫「transcript 只有 nightly 本身」）。學習來源改以**已 push 上 GitHub 的 git commit messages**為準，別假裝分析不存在的 session。
* **全域設定：routine 只建議不自改；通知靠「NOTIFY 檔＋session-start 浮出」**：用戶定調——夜間 routine **可自動加性更新 lessons，但全域設定（GLOBAL.md/SSOT 設定檔）只能「建議」、不得自行修改**（改動權保留給用戶）。建議 append 到 `_context/nightly-notify.md`（commit main，且 commit 只 `git add` 加性檔、不 `-A`，確保設定檔不被誤提交）→ 本機 hook pull → **session-start 開場讀此檔、有未勾項就提醒用戶核准**（靠 `wtf-root.txt` 錨點任何專案都讀得到）。用戶「一坐下就看到」、漏不掉、零外部設定，且**自動不越權改設定**。
* **routine 別碰會被自動產的產物**：舊 nightly 手改 `dashboard.html`，但儀表板已改本機 `sync_config.py dashboard` 自動產 → routine 不該再維護它（雙真相源）。自動產的產物由產生器負責，排程只碰它「唯一來源」的東西。

## 2026-06-03 (全域技能精簡 12→10 + 刪檔鎖定)

* **技能精簡：規則型 skill 併回 GLOBAL.md，輸出型 redundant skill 刪除**：GLOBAL.md 步驟四（>10 全域 skill）觸發。`tasklog-naming` 本質是規則（命名/結案/INDEX-TaskLog 分工）且大量重疊 GLOBAL.md → 併回 GLOBAL.md（每次必載、單一來源，比 skill 更不漂移），session-start/session-end 引用改指 GLOBAL.md。`cowork-start`（輸出 Cowork 開場 URL 貼文）與 CLAUDE_COWORK.md 既有自含開場段重複、且用不穩的 raw URL → 直接刪。12→10。**移 skill 要連帶清四處引用**（GLOBAL.md 指標、兩 skill 內文、skills-install 清單）。
* **`git rm` 留空目錄；sync 把空目錄當 skill**：`git rm -r skills/X` 只刪追蹤的 `SKILL.md`，**空目錄殘留**（git 不追蹤空目錄），`sync` 的 `iterdir()+is_dir()` 仍把它當 skill 部署。移 skill 要 `git rm` 後**再實體 `rm -rf` 空目錄**。
* **Windows Python `shutil.rmtree` 被鎖（WinError 5），bash `rm -rf` 可繞過**：部署副本（`~/.claude|.codex|.gemini/skills/`）的舊 skill 被本機程序鎖定，Python `rmtree` 噴 `WinError 5 存取被拒`（同 ai-team 老坑）；改用 Git Bash `rm -rf` 同一路徑**成功**（不同 syscall/共享模式）。故 sync 的 prune 用 Python 會在鎖定時略過（下次未鎖再清），要即時清改 bash rm。
* **deploy_other_tools prune 守門靠 rmtree 拒刪 symlink**：codex/gemini 的 `find-skills` 是 symlink；Windows MSYS symlink 的 `Path.is_symlink()` 偵測不可靠，故 prune 不靠它，改「dotted 跳過 + rmtree 對 symlink 自然拒刪 + 例外靜默」三層守。

## 2026-06-03 (跨工具 skill 部署 + monitor 啟動時機)

* **跨工具 skill 部署：實體複製＋保留工具自有 skill＋不 prune**：WTF 共用 skills 原只進 `~/.claude/skills/`；擴 `sync_config.py` 的 `deploy_other_tools()` 也部署到已安裝的 Codex（`~/.codex/skills`）／Gemini（`~/.gemini/skills`）。**關鍵兩坑**：(1) 這些工具的 skills 夾有自己的 skill（如 `find-skills` symlink 指 `~/.agents/skills`），故**只加 WTF skills、不可套用 ~/.claude 那套「prune SSOT 沒有的舊 skill」邏輯**（會誤刪 find-skills）。(2) 用「base 夾存在才部署」判斷工具是否安裝（`~/.codex`/`~/.gemini` 存在），跨平台同碼（Mac pull+sync 自動部署到它有的工具，免分支）。取代舊 symlink `sync-skills.sh`（symlink 禁律）。
* **常駐 monitor 只在密集跨機協作才開**：Drive per-machine `signals_*`＋雙方常駐 monitor 成本高（鎖檔/漏訊風險），**只在 `ai-team`＋使用者明示「跨機討論」時啟動**。一般交棒：處理完更新 `INDEX`/`TaskLog`，對方新對話開場自然讀到（非同步），不開 monitor。已寫入 GLOBAL.md Multi-Agent 底線。

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
