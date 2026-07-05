# 全域 Lessons 索引（雲端 SSOT）

> 跨專案教訓的單一檢索入口。隨 git 同步至所有機器。
> **這是指標，不是副本**：每條只放「專案｜日期｜一句話｜連結」，完整內容留在工作層檔案，避免雙真相源。
> 工作層新增 lesson 後，須同步登錄一行到此表（見 `GLOBAL.md`「教訓兩層」）。
>
> 連結為相對路徑：Drive 專案自 `Claude_cowork` 根起算；WTF 自身已移出 Drive，連結標「（WTF repo）」者相對 WTF repo 根。

---

## 跨專案通用（高重用，優先參考）

| 專案 | 日期 | 一句話 | 連結 |
|---|---|---|---|
| WTF | 2026-07-05 | SessionStart hook 注入式設計：直接 cat 三檔內容灌 context（提醒式靠 model 自覺=不可靠）；hook 輸出加識別首行做目視生效驗證 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-07-03 | mission-loop 自主迴圈設計：cron=UTC 陷阱（實證）/QUEUE 狀態整欄精確比對/分鐘偏移避對撞/定錨棒防漂移/升級能力需實證閘 | `wtf-config/playbooks/mission-loop.md` |
| WTF | 2026-07-03 | Fable5 制度建置：常載鏈瘦身（三檔制開場、制度層路由、playbooks 按需檔）＋派工/判斷/交辦/維護四守則；動手前先過 GLOBAL.md「制度層」 | `wtf-config/playbooks/`（總覽見 `letter-from-fable5.md`） |
| WTF | 2026-07-02 | `git add` 遇壞 pathspec 整批中止、配 2>/dev/null＝靜默漏 commit；add 不遮 stderr＋commit 後核 files changed 數 | `_context/lessons-learned.md` |
| WTF | 2026-07-02 | 機器解析 git 輸出：一律 `-c core.quotepath=false`（中文檔名八進位跳脫）＋不預先全段 strip（porcelain 首行前導空白錯位掉字） | `_context/lessons-learned.md` |
| WTF | 2026-07-02 | agent 定義（~/.claude/agents/）與 skills 熱載即生效、hooks 不熱載需新 session——部署後驗證時機別套錯（實測對比） | `_context/lessons-learned.md` |
| WTF | 2026-07-02 | dogfood 自家守門立即回本：coach 三道閘首兩用抓 3 真缺陷；「先動工後立約」違規實證時序紀律需 PreToolUse 機器強制 | `_context/lessons-learned.md` |
| WTF | 2026-07-02 | 紀律靠輸出守門 lint 機器攔截(禁詞+字數 stop_hook)不靠自律；錯誤轉 lint_rules.json 可機檢規則才複利 | `_context/lessons-learned.md` |
| WTF | 2026-07-02 | Claude Code hook 不熱載、需重啟 session 才生效(issue #22679)；跨工具紀律靠規則寫全域開場檔+輸出前自跑 reply_lint | `_context/lessons-learned.md` |
| WTF | 2026-07-02 | 視覺評分要嚴格；讓看不到圖的 headless agent 用文字描述打分＝系統性灌水（描述給7-8，PO看真圖1-2）→視覺分只能看實際截圖判 | `_context/lessons-learned.md` |
| WTF | 2026-07-02 | 「AI 助理框架」＝治 agent 的 harness(契約/自驗閘/回顧+教練制)，非預先註冊 handler 的工作流函式庫；靠結構強制不靠自律，溝通冗贅＝紀律漂移 | `_context/lessons-learned.md` |
| WTF | 2026-07-02 | 本地優先路由命中即繞過 LLM 省 API；自訂 delimiter `|` 會被 Policy Gate 當注入擋（反證有效）→改 0x1f | `_context/lessons-learned.md` |
| WTF | 2026-07-02 | 待辦架構：TaskLog=真相源、ai-team-todo App=鏡像(owner分user/AI掌握工作量)、廢 INBOX；/inbox 收尾只 add 本次 TaskLog 檔勿 add _context/ | `_context/lessons-learned.md` |
| 出勤 | 2026-07-02 | PA 提醒流程三坑：全天行事曆事件視窗要取今天單日（昨~明天窗會撈到前天全天假）；條件卡 `equals(陣列,true)` 恆 false 改 `not(empty())`；迴圈 PatchItem 後記憶體陣列是舊值、後續判斷須重讀清單。per-person 屬性存 per-task 列判「任一列有值」；Select `toLower(null)` 炸整支加 coalesce；「參考某流程」先分清是改的主體還是只抄設定的範本、能在既有流程加尾段就不另作 | `projects/出勤專案/_context/lessons-learned.md` |
| 出勤 | 2026-06-16 | 低代碼儲存選型：唯讀＋小表（<2000列）＋低頻走 Excel 直連(須Table；如請假餘額/team_member，建清單反多餘)；多人並發寫＋需欄位/項目權限＋可能累積的走 SharePoint 清單(如出勤主檔：員工填回覆+行政填狀態+自動寫入三方並寫、實際出勤狀態要員工唯讀)——Excel 會鎖檔/覆蓋、無欄位權限、非委派2000列頂；按讀寫特性分流，非全清單或全Excel | `projects/出勤專案/_context/lessons-learned.md` |
| 出勤 | 2026-06-14 | 舊交接記的環境限制（「Power Apps YAML 無法貼入」）要再驗別當永久前提：官方 pa.yaml paste code 新功能上線後實測可貼入並執行，舊結論是當時舊格式的；過時前提會讓整條路線繞遠路 | `projects/出勤專案/_context/lessons-learned.md` |
| 出勤 | 2026-06-24 | Canvas gallery 逐列自動存：OnChange 寫回的「無限迴圈+通知洗版」根因＝控件 Items 沒載入→Selected 空→無 guard 不斷寫空值；修＝穩定控件(DropDown@2.3.1+Items.Value)+三重 guard(空/預設/值未變不寫)+`AddColumns(... As alias, LookUp())` 預 join 現值供 Default(巢狀 LookUp 引外層用 As 別用 ThisRecord)；pa.yaml 控件版本只用使用者匯出出現過的；Windows PS 叫 codex/agy 長 prompt 含雙引號要走 stdin(`Get-Content -Raw\|codex exec -`)非 $var 直傳 | `projects/出勤專案/_context/lessons-learned.md` |
| ai-team-todo | 2026-06-15 | Supabase 新金鑰(publishable/secret 在 Settings→API Keys)；個人單用戶 magic link 會撞寄信限額/Gmail預掃吃token→改 email+password(admin API 建帳號)；公開靜態部署只傳 build 子集排除機敏檔，Cloudflare Pages 未知路徑回 index.html(200) 驗洩漏要看內容非 HTTP code；DDL 不能用 secret key 跑(需 SQL Editor)；RLS 單租戶要 email allowlist | `https://github.com/coldjokenewbie-code/ai-team-todo` `_context/lessons-learned.md` |
| CDIC | 2026-06-11 | 擋全域輸入掛 window capture 不掛 document（同節點同相位照註冊序，攔不到更早註冊者）；驗收要驗「過程中從未動過」(MutationObserver) 非只驗最終狀態；Playwright mouse.wheel 可能無效改合成 WheelEvent、觸控用 CDP dispatchTouchEvent | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-06-11 | Windows 免 Android Studio 建 APK：JDK 用 Temurin ZIP（MSI 卡 UAC）、licenses 寫 hash 檔跳過互動、packageDebug tmp 鎖清 incremental 重跑；build 失敗後禁接 adb install（會裝回舊 APK，必驗 versionName）；PS5.1 .ps1 必須 ASCII/BOM；`>` 重導 adb 二進位會毀檔 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-06-11 | kiosk 區網部署 checklist 必含防火牆：Public profile 預設擋入站且 headless node 不跳允許視窗（localhost 全通、外部全斷零錯誤訊息）；平板端 `adb shell toybox nc` 驗連通；同步測試 guide 是唯一真相源、手動 POST 會被其輪詢蓋掉 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-06-12 | Tabby 貼不了剪貼簿圖→agent 端 PowerShell [Clipboard]::GetImage() 抓檔再 Read；cp950 主控台禁 print CJK 再 redirect，一律 python 內寫 UTF-8 檔 | projects/cowork_CDIC/_context/lessons-learned.md |
| CDIC | 2026-06-12 | 同一 PDF 各頁色值不同先查 ICC（extract_image cs-name），取印刷標準 profile 當標準值；背景研究 agent 要求增量落盤（截圖隨抓隨存保住、規格書押尾全失）；劇照含烘焙標題字須裁切專用素材當封面 | projects/cowork_CDIC/_context/lessons-learned.md |
| CDIC | 2026-06-12 | 翻頁式 HTML（fixed viewport+track）驗收用鍵盤逐頁導航+viewport 截圖，off-screen element screenshot 不可靠；橫滑與頁內捲動併存：dx>14 且 dx>1.3dy 才接管+touch-action:pan-y | projects/cowork_CDIC/_context/lessons-learned.md |
| CDIC | 2026-06-17 | 多機撞車止損：`git commit` 提交整個 index 非你剛 add 的檔→commit 前必 `git diff --cached --name-only` 核對（工作樹開場髒時別整碗端走，別人變更先 stash）；多機平行同一展區動工前先認領 canonical 路徑/版本（查 commit byline+INDEX+`git ls-files` 對照磁碟），勿在改名前孤兒夾做整輪工 | projects/cowork_CDIC/_context/lessons-learned.md |
| WTF | 2026-06-17 | session-start python 平台選擇：環境 block 有 Platform 欄位，Mac/Linux=`python3`，Windows=`python`；寫死任一在另一端報 command not found → 讀 Platform 動態選指令，hook 腳本同理 | `_context/lessons-learned.md`（WTF repo） |
| 國圖南 | 2026-06-17 | 自動逾時計時器(setTimeout)要在「離開該狀態的每一條路徑」都清除：outro outroTimer 只在 goIdle 清、goSelect 沒清→調版中途誤觸跳待機；單輪流程測不出，需多輪連續 Playwright 才驗得到 | `SouthLibrary/_context/lessons-learned.md` |
| 國圖南 | 2026-06-17 | 圖內 baked 文字替換法：用同背景色補丁（absolute overlay）疊蓋，`min-width` 確保完全蓋住（新標籤可能比原文字短），截圖驗證沒殘字露出 | `SouthLibrary/_context/lessons-learned.md` |
| CDIC | 2026-06-16 | 曲線導引版面：要「曲線穿過內容節點」且內容長度不定→JS 依節點 DOM 實位繪 path（非硬算座標），配 document.fonts.ready／ResizeObserver／beforeprint double-RAF／尺寸 0 guard 防 NaN；風格「沒做到」根因常是版面骨架（分塊 vs 路徑導引）非外觀；base64 內嵌縮圖防破圖但 loading=lazy 對離屏 data URI 自驗假陽性；codex exec 要 `<\ /dev/null` 關 stdin、agy --print 在非 TTY 吐空改 GUI 非同步（見竹科教館 node-pty 解）；heredoc 吃 JS `\\` 改 pathToFileURL | projects/cowork_CDIC/_context/lessons-learned.md |
| 竹科教館 | 2026-06-10 | ai-team skill 指名的 cli-reference.html 動工前必讀；鐵則「被呼叫 agent 只輸出文字、不讀寫檔，Tech Lead 把內容餵進 prompt/stdin」；第一次失敗即回查指名文件，勿試 bypass/換 shell/怪硬碟等臆測繞法 | `projects/HsinchuScienceEducationCenter/_context/lessons-learned.md` |
| 竹科教館 | 2026-06-10 | agy headless 在 Claude 工具中需 node-pty 建 ConPTY 才會輸出（偵測非 TTY 就空輸出；winpty/pywinpty 本機失敗）；`--dangerously-skip-permissions` 必加；輸出含 ANSI+重繪重複行需清理；外部 agent 結論仍須逐項回查驗證 | `projects/HsinchuScienceEducationCenter/_context/lessons-learned.md` |
| WTF | 2026-06-09 | 判讀/指派工作紀律：①無證據絕不硬湊（找不到依據標「未知」交審，禁「挑個附近沒用到的」填值）②先建高對比/可追蹤檢視再判定（缺工具就肉眼瞎猜＝高錯誤）③鄰近≠連線、高信心幾何(端點距≈0)不得被肉眼印象推翻 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | 互動 HTML 交付前用 headless playwright 自驗（掛 pageerror/console listener+click 斷言互動），抓「畫面對但互動壞」；專案沒裝 playwright 走全域絕對路徑 require；file:// 開中文檔名先 URL-encode | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | ai-team cli-reference 按角色分段：各 agent 只讀自己那段（Codex TL/Antigravity TL/Claude TL），共用概念獨立一節，降低 context 耗費 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | sync_config.py deploy_other_tools() 只清 symlink、不清實體舊檔；換機/重裝後 stale 實體舊檔需手動清（已知 gap，待修）| `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | 禁止推測填入未實測的 agent CLI 規格（呼應誠實告知）：規格必須由當事 agent 實測或自報後再落檔，他方推測會把自己行為誤當對方的 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | 雲端 routine 掃多 repo 只能靠 trigger 預掛載（直連 github 無憑證、clone 必敗）；registry 增刪要回 /schedule update 同步掛載；TZ=Asia/Taipei 定義「今日」避免 UTC 切日 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-07 | 技能載入：原生已自動列 skill 名稱+描述、body 觸發才讀；開場強讀全部 SKILL.md 是疊床架屋→廢除；「>10 數量門檻」隨成本消失一併撤，改以功能重疊為精簡準則 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-07 | 跨工具：各工具認自己原生檔名（Codex 讀 ~/.codex/AGENTS.md 非 CODEX.md，實證）、用實體副本非 symlink；per-machine 部署洞要 check 驗+寫對機待辦；三工具都有 headless CLI(claude -p/codex exec/agy --print)→ai-team 同機改 CLI 直驅、信號檔降 fallback | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-16 | Claude 當 ai-team TL 實測：agy 在 IDE 內建 shell(非 TTY) 一律 EXIT0 空輸出(根因非 TTY，非登入；log 的 not-logged-in 是紅鯡魚)→換獨立終端機跑；codex exec 加 `-s read-only`(否則自跑開場觸 Win sandbox helper 報錯，但末句答案仍正常)+`< /dev/null`；`--dangerously-skip-permissions` 在 Claude Code 被 auto-mode classifier 擋 | `tools/ai-team/cli-reference.html`（WTF repo，Claude TL 段） |
| 根 | 2026-05-03 | 七步驟工作流步驟4「執行不打擾」：卡關寫 `_blocker_*.md` 跳過，不中途問頁數/換工具 | `_context/lessons-learned.md` |
| 根 | 2026-05-03 | docx 註腳用 Word 頁尾 footnote，多次引用各生獨立 footnote，直改 `footnotes.xml` | `_context/lessons-learned.md` |
| WTF | 2026-06-03 | 整個 repo 移出雲端硬碟＞只 split 子目錄；前提變了（用戶已整包移出）就重評方案、別照交接照單執行 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | SSOT 檔禁寫單機絕對路徑；repo 一搬 `parents[N]`/`relative_to` 推導全崩，改絕對 registry/SCRIPT_DIR.parent | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | Drive 跨機協調檔：每機只寫自己的檔（單寫者免衝突）；禁掛常駐 tail -F（鎖檔擋 Drive 同步），改 on-demand 讀 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | 跨工具 skill 部署：實體複製到 codex/gemini，保留其自有 skill、不 prune；base 夾存在才部署（跨平台同碼） | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | 常駐 monitor 只在 ai-team+明示跨機討論才開；一般交棒靠更新 INDEX/TaskLog、對方新對話自然讀（非同步） | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-04 | 雲端 routine commit 死分支＝自動更新沒生效；要 pull--rebase→改→push main。雲端看不到本機 transcript，學習靠 git commit | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-04 | 雲端→用戶通知靠 NOTIFY 檔(nightly-notify.md)+session-start 浮出（wtf-root 錨點），零外部設定、漏不掉 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-04 | 跨工具部署：dangling symlink（舊架構死連結）被誤當工具自有保留、擋 copytree（Errno 17）；複製前拆同名 symlink。sync 報「寫入N個」N≠預期即沒全成 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | 技能精簡：規則型 skill 併回 GLOBAL.md、redundant 刪；移 skill 要清四處引用+git rm 後實體刪空目錄 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | Windows Python rmtree 被鎖(WinError5) 改 bash rm -rf 可繞過；MSYS symlink is_symlink() 不可靠靠 rmtree 守門 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | 跨機 AI 協作＝共用檔案＋雙向 monitor（grep 限定 [TAG-R數字]、prev 設啟動基線避免自觸） | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-06-03 | Drive 同步 .git 跨機不可靠→各機自己 add、單一端 commit，另端 reset 淨空 index | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-06-03 | 設定檔自動執行 hook 屬自我修改，classifier 擋需用戶明授；破壞操作別繞過改靜態驗收 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-06-03 | sync_config.py 全域部署用破壞性 rmtree，Windows 遇 skill 鎖定（ai-team）整批失敗；改逐 skill 容錯覆蓋 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-06-02 | 接手時交接待辦狀態用 git/檔案實況核對，不照單全收文件陳述（可能過時） | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-05-24 | 溝通原則硬限制（禁「您」、回應字數上限）有效降 token、防發散 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-05-24 | 開場「已載入設定」一個 session 只報一次，後續直接進主題 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-05-24 | ⚠️已被推翻：原 symlink 去中心化方案，因 Drive 不支援跨平台 symlink 改為實體同步（見 `sync_config.py`） | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | ⚠️已被推翻(2026-06-07)：Cowork 現可讀外部 URL（實測 fetch raw.githubusercontent 成功）→ Cowork 全域設定改填 CLAUDE_COWORK.md raw URL 自動載入，不再每次貼入 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | 分工：Cowork 讀寫本機/批次/長流程；Claude Chat 網頁瀏覽/WebSearch，互補不互換 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | 簡報/文件大綱先問實際過程再動筆，禁依主題名稱臆測內容 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | PRD 與 Prompt 功能不同不重複；Prompt 只放執行端所需，細節留 PRD | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | 專業術語以使用者提供定義為準，不自行推斷 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | WorkLog/Handover/lessons 三檔分工：做了什麼/接手做什麼/下次記得什麼 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | git commit 前查 `--cached --stat`，排除 node_modules/runtime/>100MB；超大檔 `git rm --cached` | `projects/cowork_CDIC/_context/lessons-learned.md` |
| HsinchuSEC | 2026-05 | 驗證不能只看腳本「Done」，必須截圖確認實際顯示才算驗收 | `projects/HsinchuScienceEducationCenter/_context/lessons-learned.md` |
| HsinchuSEC | 2026-05 | 論點必須有實際數字支撐，不可用結構推論代替數據 | `projects/HsinchuScienceEducationCenter/_context/lessons-learned.md` |
| 國圖南 | 2026-05 | 量不準先換手段：抽 pptx XML 會被 group transform 干擾，改算繪成圖再量測 | `projects/國圖南/_context/lessons-learned.md` |
| 國圖南 | 2026-05 | 並行 repo commit 只 stage 自己任務的檔，勿 `git add -A` | `projects/國圖南/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-04 | 可微調文字位移用 margin 不用 transform：fill:both 進場動畫/translateY(-50%) 會壓過 inline transform | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-04 | SVG 裝飾網格灰點只能在 ≥2 線匯聚處：寫腳本點到線段距離測試驗證、新線平行既有方向、線端出血避免懸空 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-04 | File System Access 存檔報 user aborted＝取消選擇器非 bug；選同一檔允許寫入、handle 存 IndexedDB免重選 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | docx 同格雙語：deepcopy 中文段→換 w:t→addnext，保留 compress_type；⚠ 欄名可能與實際內容錯位，先看哪格有字 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | 新增同類元素避開既有編輯器固定計數(count:3)，改用獨立 class；白字配暗 text-shadow 提升淺底圖對比 | `_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | CJK 全形字寬≈1em、拉丁數字≈0.5em，「同字級≠同寬/同視覺」；兩行等寬須反向調字級，變動字數需 JS 動態算 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | 多行區塊跨欄 baseline 對齊：兩者用相同 line-height 行框 + Range.getClientRects 量 bottom、margin-top 微調校到 0-3px | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | 「留白/靠上排列」常是設計取捨非 bug，先確認再動（自作主張改 flex 撐滿被否決） | `projects/cowork_CDIC/_context/lessons-learned.md` |
| WTF | 2026-06-05 | Session 啟動必須強制執行 wtf-config/sync_config.py check 與標準身分宣告，不可等用戶指示 | `_context/lessons-learned.md`（WTF repo） |
| cowork_CDIC | 2026-06-09 | 視覺驗收必須新舊疊圖 pixel-diff＋大面積純色定點取樣；只看新版好不好看會漏整片底色差(D區 P2/P5/P6 灰vs橘)；vision-based agent 漏純色差、像素取樣才抓得到；高頻照片區 diff% 是假象需 band 定位區分 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-09 | 「視覺僵硬」≠微調問題：根因常是版面構成（全左靠=行政表單感），AI 多輪微調救不回來；先根因診斷再換構圖重做一版；多 AI 獨立評比交叉驗證可提高 PO 採信度 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-09 | CSS/SVG 優於 mp4 做規矩進場動畫（淡入/描線/位移/序列）；mp4 代價：解析度鎖死/首屏等載入/字體烘焙/雙份維護漂移/autoplay 風險；mp4 真正出場=粒子/流體/3D/生成式光影/真實影片素材 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-10 | PO 要放大/延伸既有視覺素材時禁自生成新藝術替換，沿用原素材「複製既有元素平移補位」延伸(波紋連退三次教訓) | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-10 | 「任何方向都觸發副作用」需求當心邊界 early-return 吞掉它(解除暫停放邊界判斷前)；驗收要含邊界案例 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| Asembly_PPT | 2026-06-10 | python-pptx 換圖零變形＝frame 比例必須=截圖比例(圖片 stretch-fill 整框)，保高度調寬度置中；換圖用 blip rEmbed 重指向新 image part 且先清 a:srcRect 免誤裁；Win 無 soffice 改 PowerPoint COM Slide.Export 算繪驗收；app 截圖注入 CSS 隱藏 dev toolbar，fullPage 會讓 fixed bottom nav 浮頁面中段→改標準 viewport | `projects/Asembly_PPT/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-10 | kiosk 多裝置同步：狀態同步(傳JSON各機自渲染)優於畫面廣播；Node SSE必加 Cache-Control:no-store 防 kiosk 快取「改了沒生效」；動畫 func early-return 被吞需雙保險(事後硬切+每350ms reconcile 自癒)；Android WebView file:// 需 INTERNET+cleartext+universalAccess；macOS build APK=openjdk@17+commandlinetools+gradle-wrapper 釘版 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-10 | 大量外站擷圖批次管線：容錯腳本逐站不中斷+WebGL 動態站等待 9s+cookie 牆換乾淨源；PNG 轉 JPG 瘦身(sips 或 playwright type:jpeg quality:80)；file:// 本地頁用 JS 變數(window.DATA=...)替代 fetch json 免 CORS | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-12 | 素材需求清單縮圖欄＝素材原圖非畫面裁切；溯源必查業主簡報 pptx 內嵌媒體(zipfile 抽 ppt/media，「找不到」的圖多在簡報裡)；檔案歸屬靠位置+轉檔目視雙驗證(HEIC 歸屬翻案)；審查 HTML 用相對路徑免 localhost；Win 無 soffice 用 Word COM 轉 PDF 驗收；多 AI 平行只 add 自己的檔 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| 南科再生水廠 | 2026-06-12 | 實體互動板設計迭代若只停在「換機制名字的提案簡報」層，等於卡住：需拆出「現場流程劇本」（誰拿/何時揭曉）＋「1:1 板面設計稿」兩個交付物；六指標框架（全員參與/誤導揭曉/發光活用/知識連結/耗材歸零/張力持續）逐版填表可快速定位致命缺陷 | `projects/南科再生水廠/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-15 | E區投影牆波浪車道：canvas 裁 bbox(alpha>16)再置中；postMessage+BroadcastChannel 雙管→時間戳 t+lastT 去重；緩動用 smootherstep(6t^5-15t^4+10t^3)頭尾不突兀；平行波浪=同波項+差 base→永不交叉，±15%速差破整齊；波長太長≈直線(需畫面含 1.5 個起伏)；焦點元素給專用車道+從最右端進=零碰撞；動畫程式化取樣逐幀 getBCR(x,y)驗弧線+減速；kiosk 高來回→常數三組獨立命名(AMP/WL/ENTER_MS/速度因子)方便逐項微調 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-16 | 多團隊並行 repo 原子 add+commit：`git add` 後 staged 暴露給全 repo、別組 commit 會帶走→`add <自己檔> && commit` 一個 Bash call 內完成（縮短暴露窗）；commit 前 `diff --cached --name-only` 核對只含自己的檔，夾帶別組檔先 `reset` 再精準加 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-16 | 電子書手機→桌機 RWD 三坑：①scale-to-fit `overflow:hidden` 殘留擋捲動（html 唯一垂直捲容器、body `overflow:visible`、`overscroll-behavior:auto`）②ken-burns `scale` 溢出須在直接容器加 `overflow:hidden` 裁③同特異度後者蓋前者破版需確認宣告序；前台文字編輯通用做法：葉節點 `contenteditable`+`data-ek` key；「存為預設值」＝File System Access 寫回 HTML `<script id="eb-defaults">` 任何裝置都讀得到；Content Pack+subagent 分版保文案一致不重複擷取 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| 出勤 | 2026-06-22 | Power Automate 四大坑：①運算式必用「fx token 插入」(直接打字變字面字串，症狀：輸出整段運算式文字)②SharePoint 欄「內部名≠顯示名」(中文欄常成 field_N，從執行 JSON key 確認)③Condition 無進階模式→左值用 fx、右值 fx 打 boolean true(直接打 `true` 是字串→永遠 false)④連動改有順序依賴：資料源→迴圈來源→內層運算式 | `attendance-dashboard/_context/lessons-learned.md` |
| 出勤 | 2026-06-22 | 接手既有 Power Automate 流程先解壓匯出 zip 的 definition.json：真 action 名/欄繫結/URL/連線參照全在裡面，一次坐實病灶(「Select 映 null＝欄內部名是 field_3」等)，讓指南用真名寫、可直接照改 | `attendance-dashboard/_context/lessons-learned.md` |
| 出勤 | 2026-06-22 | 同 repo 兩個 Claude CLI 並行：各 `git worktree add` 獨立目錄+分支，working tree/index 完全隔離不互踩 `git add`；共用紀錄檔(TaskLog/lessons)改「各寫各的新檔」避免 merge 衝突；各自完工後 merge main（後者先 pull） | `attendance-dashboard/_context/lessons-learned.md` |
| 出勤 | 2026-06-22 | 採納外部 agent(Codex)建議要用自有系統知識守門：Codex 不知專屬架構(如 Planner2Line 路由靠主旨，To 必須是中繼信箱)，涉及專屬系統的建議 Tech Lead 須以掌握的架構否決，不照單全收 | `attendance-dashboard/_context/lessons-learned.md` |
| CDIC | 2026-06-23 | 交付文件必先問「給誰看」：給程式開發團隊只給 asset 檔名+結構，拿掉業主端內容（出處/來源/審稿/索取管道）；用語「廠商→開發團隊」「網站→多媒體展示項目」—— PO 連退數輪才 OK | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-06-23 | iPhone HEVC(hvc1) 在未裝擴充的 Chromium videoWidth=0，但 readyState=4/err=null/時長正常→極易誤判正常；判定要看 videoWidth>0 且查 fourcc(avc1/hvc1)；ffmpeg h264_videotoolbox 轉碼＋保留原檔名＋原檔移 OLD 備份 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-06-23 | Playwright 驗影片/圖兩大假象：①`page.setContent` 是 about:blank origin→file:// 影片回 err4 假失敗，需用真實 file:// HTML；②只滾到頂再數 naturalWidth=0 被 lazy 圖假陽性，判前須先全頁滾動觸發 lazy | `projects/cowork_CDIC/_context/lessons-learned.md` |
| 出勤 | 2026-06-24 | Power Automate「更新項目(PatchItem)」不要填 Title，否則報「Item/Title 已不存在於作業模式中」孤兒參照（Save As 複本帶失效繫結／Title 改過顯示名 schema 無此 key）；修法＝直接移除 Title 那格即可，不必整個動作重建。更新用 id 定位既有列、Title 留空不會被清空；只有「建立項目」才必填 Title（兼唯一鍵） | `attendance-dashboard/_context/lessons-learned.md` |
| 組立導覽 | 2026-06-24 | 博物館導覽 App 定位：導覽≠策展（導覽是中介既有展場、不創造新敘事，別把貫穿主線/旅程隱喻當導覽）；實體展已是沉浸主秀(機具劇場/剖面動畫/燈光秀/導覽員)時 App 別複製內容或做奇觀＝跟實體+真人搶注意力且必輸，價值在散客缺口(逐人化/帶路/記憶)；鉤子屬展項本身、豐富(AR/音訊)只過三缺口閘(物件不在現地/看不見聽不到/時間維度)；帶路＝空間+內容+服務三維(有意圖拉/無意圖推同引擎、預設推拉一鍵)；音訊優先但須文字雙軌(否則擋聽障)、觸發用編號鍵入勝QR；舊投標規劃(人×事×物/RFID/Beacon)製作期須重新核對非規格 | `Assembly_Plant_Mobile_Guide/_context/lessons-learned.md` |
| 出勤 | 2026-06-24 | SharePoint 清單文字日期欄排序陷阱：格式 `yyyy/M/d`（非零填補）文字序錯位（`2026/12/1` 排在 `2026/3/2` 前）；改用 Title=`yyyyMMdd_…` 固定寬度零填補鍵，文字序＝時間序，最新置頂且對回填列亦正確；**設計時識別/排序鍵一律零填補固定寬度字串** | `attendance-dashboard/_context/lessons-learned.md` |
| 出勤 | 2026-06-24 | git worktree 資料夾是本機產物、不隨 remote 同步；跨機只能靠分支+commit 重建（離機前 push，新機 `git worktree add <路徑> <branch>` 重建）；重建步驟寫進 INDEX.md 頂段，讓新機 Claude 看到 main 即主動協助 | `attendance-dashboard/_context/lessons-learned.md` |
| CDIC | 2026-06-24 | Playwright screenshot 去背：`omitBackground` 只關瀏覽器預設白底、不移除元素自身背景色→須同時設 `html,body{background:transparent}`；截疊層元素前須對祖先鏈強制 `opacity:1;transition:none`（祖先 opacity:0 合成後子元素不可見，即使子元素本身不透明） | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-06-25 | Playwright `page.pdf(preferCSSPageSize:true)` + `@media print { @page { size: WxH } .slide { overflow:hidden } .track { position:static } }` → 手機網頁轉乾淨 N 頁向量 PDF，繞過瀏覽器頁首頁尾，頁數等於設計頁數；`position:fixed` 元素在 print 模式脫離文件流需改 static，否則頁數爆增 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-07-01 | E區瀏覽交付規格去冗文：外包只給「元素+位置+檔名」，移除過程/說明/補充；照片相框等正式編號元件（C14–C18）縮圖一律「編號+名稱+檔名」；可編輯存檔保留工具列/腳本（只移 contenteditable）；去機台黑遮罩=像素對齊背景硬覆蓋+遮罩充分膨脹15px吃掉抗鋸齒暗邊 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-07-01 | Drive git 多機並行：`GIT_INDEX_FILE=/tmp/idx + git read-tree origin/main → add自有檔 → write-tree+commit-tree+update-ref` 繞過共用 index 暫存吞噬＋cloud-only 逾時；`.git/logs/HEAD` 等未落地檔 `rm` 讓 git 自重建（只丟 reflog，安全）；白名單制 `/*` 新頂層夾須 `git add -f` 才進版 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-07-02 | AI 評審（subagent 打分）系統性高估 3-4 分，不得當交付門檻：AI 評審只取修改清單、分數無效；唯一有效門檻＝PO 本人給分 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-07-02 | 「風格對了但分數不動」＝媒介天花板（Canvas 2D 上限≈4-5），別再同法迭代；跳級需真素材（AI 生圖/授權圖紋理）或 WebGL 渲染 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| CDIC | 2026-07-02 | Drive .git loose objects 雲端抽離致 commit 卡死：objects 被 Drive 同步為 cloud-only 後 git 無法解壓，需另機 sparse clone 或等落地，不嘗試 repair | `projects/cowork_CDIC/_context/lessons-learned.md` |

---

## 專案專屬（詳見各專案 lessons-learned.md）

> 專屬細節不複製到此，僅列主題索引供發現。

| 專案 | 涵蓋主題 | 連結 |
|---|---|---|
| cowork_CDIC（CDIC 存保史料館） | 術語參照表優先、展品編號來源、年表整合、歷史照片來源、LibreOffice 渲染、素材主題真實相關、文案權威來源、三欄卡片版型、kiosk 互動、Playwright 視覺驗收、PPT QA 用 subagent、批次截圖固定寬、版面構圖診斷、CSS vs mp4 動畫判準、kiosk 簽名 canvas dpr cap、多裝置同步(狀態vs廣播/SSE/APK 建置)、外站擷圖批次管線、投影牆波浪車道動態(smootherstep/平行車道/程式化動畫取樣驗收)、多團隊並行 add+commit 原子化、手機→RWD scale-to-fit 陷阱(html 唯一捲動容器)、ken-burns 直接容器裁切、前台 contenteditable 編輯器(葉節點+data-ek)、File System Access 存為預設值(寫回 HTML)、Content Pack+subagent 分版、交付文件分對象(業主端vs開發團隊)、素材包分版(內部完整v1+冪等gen v2)、iPhone HEVC→H.264 轉碼、Playwright file://影片假失敗/lazy圖假陽性/omitBackground去背/祖先opacity鏈、大型素材包靠 Drive 同步不推 git、3.6MB minified HTML 外科改動(replace_once+div平衡計數)、中翻英對照表從目標檔抽 key、B/C/E區中英對照 docx 製程、Playwright page.pdf+@media print 手機網頁→乾淨 N 頁向量 PDF(fixed→static/preferCSSPageSize)、E區瀏覽交付規格去冗文(外包只給元素+位置+檔名)、可編輯存檔保留工具列/腳本、去機台黑遮罩(像素對齊硬覆蓋+遮罩膨脹)、Drive git 臨時 GIT_INDEX_FILE 多機提交不污染共用 index、白名單制新頂層夾須 git add -f | `projects/cowork_CDIC/_context/lessons-learned.md` |
| HsinchuSEC（科教館） | docx 多腳本執行順序（lxml 先字串後）、Word paraId 重生、雙螢幕截圖座標、FTE 與人頭數分標、面積非員額決定因素 | `projects/HsinchuScienceEducationCenter/_context/lessons-learned.md` |
| 國圖南（SouthLibrary 互動展項） | PPT 頁碼會變動以內容為準、直書版面對位心法、字級名目pt≠render px、編輯模式存檔機制；互動展項：自動逾時計時器需在每條離開路徑清除（多輪 Playwright 才驗出）、baked 文字補丁疊蓋法、版面變形器(outro 結尾頁/待機 idle.png)、B-7-1 與書相遇(資料驅動場所底圖/感應台循環)、多展項並行只 stage 自己的檔 | `SouthLibrary/_context/lessons-learned.md` |
| ppt_map_mark（PPT 拉線標註） | PPT COM 自動化匯出 PNG、跨頁底圖 bbox 座標對位（srcRect+group transform 正規化映射）、引線起點=文字實際結尾（Range/像素掃描）、定位法定案（染紅渲染+綠遮罩+td編號）、孤兒 pin 禁距離硬指派、工作紀律（無證據標未知/先建驗證視圖再判定）、圖示色塊用圖例 prstGeom（別預設方形）、xlsx 刪內嵌圖須清 ws._images（openpyxl round-trip 會保留圖）、Excel 多工作表+地圖舊編號≠資料表須標題比對 | `projects/ppt_map_mark/_context/lessons-learned.md` |
| Asembly_PPT（導覽 app 簡報） | python-pptx 換圖保位置(blip rEmbed+清 srcRect)、ppt 圖片零變形(frame 比例=截圖比例)、PowerPoint COM 算繪驗收、Playwright 截 app 隱藏 dev toolbar、fullPage vs fixed 元素 | `projects/Asembly_PPT/_context/lessons-learned.md` |
| 南科再生水廠（環教中心展示） | 回顧型互動別做成記憶測驗、別把前段已強調的點當最終驚喜、PO要「有技術+要思考」≠記憶(給新問題用原理推)、ai-team 中 Antigravity headless(agy --print)非TTY回空只能走信號檔異步、Codex headless 直驅(< /dev/null)、D-4 Excel 勿過 LibreOffice recalc | `projects/南科再生水廠/_context/lessons-learned.md` |
| Assembly_Plant_Mobile_Guide（組立工場導覽 app） | 2026-06-28：app 為「重映射 token」淺色主題（寫 UI 前讀 index.html tailwind.config+:root；zinc-*=表面色、gray-*=文字色、zinc-100..500 未覆寫=近白會隱形）、「文字沒渲染」先排查色對比、「加按鈕≠重寫整頁」保留原沉浸式底圖版面增量插入、agy headless 在 Claude Code Bash tool 可正常出字(cli-reference 非TTY警告不適用本環境)、改 UI 逐項 Playwright 截圖比對；2026-06-29（UI微調+根目錄整理）：單點樣式需求只動該屬性(有副作用才回報、不自決背景)、沉浸式 hero 負 mb 把 main 整塊往上拉(非 hero 負 margin-top，會被 overflow-y-auto 裁)、tsconfig exclude 必補 node_modules(不補會掃爆)、共用 nav 字串改名牽底部nav/漢堡/頁首三處+uppercase 會把中文顯示成大寫英文、macOS git 卡 Xcode 授權時直呼 CLT 路徑 `/Library/Developer/CommandLineTools/usr/bin/git` 繞過；2026-06-29（首頁三屏 scroll-snap）：snap container 要實測 scrollTop/clientH 確認是誰在捲(main 有 overflow-y-auto 但高度被撐滿=不捲，實際是 html)、用 `:has([data-home-snap])` 只對首頁把 snap-type 掛在 html、滿版 snap 內容底部被 fixed nav 蓋用 pb-28 留白、改 tab 前逐一問清既有功能真實語義(「語音」=口述歷史非TTS)、展覽場域 icon 用線條上色非實心圓底(沉穩>鮮明)、imageUrl 占位 + onError hide 破圖靜默=素材缺口非程式bug(先 ls 驗檔)、vite port 浮動需看 log 確認實際 port；2026-06-30（Erecting 正名+AR tab 塌陷）：`absolute inset-0` 整層疊圖元件嵌入前確認父容器有可解析高度(固定px/vh)、別只靠 h-full 往上鏈式索取（`ARPage` 塞進無限高 flex 容器→塌 0、tab 空白，外包 `h-[72vh]` 修復）；官方專有名詞正名只改 `en` 欄、不碰 `tw/jp/id/key/檔名`（Erecting Workshop 正名只換顯示層 en 字串，動 key/檔名會壞路由+資產，四處共用須一起掃）| `Assembly_Plant_Mobile_Guide/_context/lessons-learned.md`（本機路徑） |
| 出勤（attendance-dashboard） | Power Apps/Power Automate 平台踩坑(運算式fx token/欄內部名field_N/Filter array相對迴圈/Select型別/Condition布林/連動改順序/OData $filter限制/convertFromUtc/Email欄型別/GroupBy v3語法/pa.yaml一畫面一檔/app不跑錯欄實為來源資料錯/UpdateItem不填Title)、接手 PA 流程先解壓 definition.json、git worktree 並行 Claude CLI 隔離（跨機靠分支+commit 重建）、外部 agent 建議須系統知識守門、PA 元件屢卡改等價更穩做法（Select去重→名冊迴圈）、沙盒 provenance xattr 問題、Canvas gallery OnChange 自動存三重 guard（DropDown@2.3.1+AddColumns As 預 join）、SharePoint 文字日期欄 yyyyMMdd 排序鍵、2026-07-03：`Text(Today(),...)` 包在 Filter/LookUp/UpdateIf 條件式內不可委派(症狀=僅委派警告，清單 append 累積破 App 非委派列數上限後才發作、修法=開場 Set 變數改比對變數) | `attendance-dashboard/_context/lessons-learned.md` |
| capture_app（macOS 類 ShareX 擷圖/錄影 app） | 2026-06-30：ai-team 三輪討論驅動原生 macOS app、TCC+bundle identity(ad-hoc 重簽重置授權/tccutil reset)、自簽憑證穩定簽章(專用 keychain+set-key-partition-list 解 errSecInternalComponent、DR 綁憑證 leaf→重建不失效、PEM 直匯繞 OpenSSL3 p12)、menu-bar-only 在瀏海溢位藏 icon=實質不可用須給 Dock+控制視窗、SwiftPM top-level @MainActor 用 assumeIsolated、ScreenCaptureKit 單張 SCScreenshotManager/sourceRect points+width/height pixels×scale、overlay sharingType=.none 防擷取殘影(對控制視窗反效果)、borderless NSWindow 預設 canBecomeKey=false(可見 key 視窗搶焦點→區域錄影壞)、Carbon RegisterEventHotKey 免 Accessibility/可自訂/錄影中動態註冊 ⌥Space·Esc、SCStream→AVAssetWriter(mp4)+抽影格 ImageIO(GIF) 停錄時序、剪貼簿 PNG+TIFF、headless --selftest-* 確定性驗證但管線 PASS≠互動可用 | `capture_app/_context/lessons-learned.md`（本機路徑） |

---

## 維護方式
- 工作中於各層 `_context/lessons-learned.md` 隨手記錄完整內容。
- 結案或 `session-end`／`lesson-add` 時，把新教訓濃縮成一行登錄本表。
- 高重用（跨專案可套用）放上區；專案專屬只在下區補主題關鍵字。
- 矛盾或過時條目標 `⚠️已被推翻` 並指向取代來源，不直接刪（保留歷史）。
