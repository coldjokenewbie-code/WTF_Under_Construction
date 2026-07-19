---
name: inbox
description: 分流語音速記 inbox。把 Obsidian Clippings 中「工作」開頭的速記分類：專案工作→該專案 TaskLog(待辦真相源)+待辦App(owner=AI 鏡像)；個人雜務→只進待辦App(owner=user)。原檔移 Ingested。專案工作另篩夜間雲端候選提名進 missions/QUEUE.md。本機手動或排程觸發。
---

# Inbox 分流（語音 → TaskLog／待辦 App）

把手機語音速記（Obsidian on Google Drive，標題「工作」開頭）分流。
**TaskLog＝待辦真相源；待辦 App（ai-team-todo）＝跨專案鏡像總覽**（owner 分「我執行=user／AI 執行=AI」讓使用者掌握工作量）。
**本機跑**（雲端 routine 讀不到本機 Drive 掛載）——可手動觸發，或本機排程（如 launchd）於固定時間自動跑。

> 快速捕捉工具，下指令後一路處理完、**禁中途問**（歸屬自行歸納）。標題式速記（正文空）是**多數常態**，標題本身即待辦內容，照常分流、別當問題回報。

## 前置：取本機資料

先讀 `~/.claude/wtf-root.txt` 取 `<WTF_ROOT>`，執行 `python3 "<WTF_ROOT>/wtf-config/sync_config.py" inbox-info`（Windows 用 `python`）。輸出 JSON：`clippings`／`ingested`／`pending`（待分流檔名）／`projects[]`（`{project,path,github,has_github}`）。

**待辦 App CLI**：取 `projects[]` 中 `project=="ai-team-todo"` 的 `path` → `<APP>`。寫入前先 `source "<APP>/tools/env.sh"`（Supabase 憑證），用 `python3 "<APP>/tools/todo-cli.py"`。先跑一次 `todo-cli.py list` 參考既有 App 專案命名（格式「領域/子區」，如 `組立/導覽`、`出勤/儀錶板`、`CDIC/A區`、`國圖南/…`）。

`vault` 為 `null` → 停下請用戶補 `wtf-config/inbox-config.md` 本機列。`pending` 為空 → 回報「無待分流速記」，結束。

## 分流（逐檔）

每筆：讀 `<clippings>/<檔名>` 全文（標題去「工作」前綴＝待辦；內文常空，標題即內容）。判**類型**：

### A) 專案工作（對應某專案／領域）
1. **判定專案**：依標題／關鍵詞／人事物對應 `projects[].project`，自行歸納，不問。多候選依關鍵詞／近期活躍度擇一。`has_github==false` → 跳過留 Clippings（列「待補 github」）。
2. **寫該專案 TaskLog（真相源）**：append 到該專案 `_context/` **最新** `TaskLog_*.md`；於其「## 📥 語音待辦」區（無則檔尾新建該標題）加一行：
   `- [ ] <待辦>（語音 <YYYY-MM-DD>・來源 Clippings/<檔名>）`
   該專案 `_context/` 無任何 `TaskLog_*` → 新建 `_context/TaskLog_<YYYY-MM-DD>_語音待辦.md`。
3. **鏡像進 App**（owner=AI）：
   `source "<APP>/tools/env.sh"; python3 "<APP>/tools/todo-cli.py" add --project "<App領域/子區>" --title "<待辦>" --owner AI --status todo`
   `<App領域/子區>` 用既有命名對齊（見前置 list；如 Assembly_Plant→`組立/導覽`、Aseembly_Plant_Interactive→`組立/互動機具`、出勤專案→`出勤`、cowork_CDIC/claude_CDIC_O4→`CDIC`）。

4. **夜間雲端候選篩（僅本步驟，不影響上面 1-3 的正常分流）**：對這筆專案工作，比照 `night-pick` skill 判準逐條檢查——全中才提名，不硬湊，多數單句速記是單一小動作、本來就不夠格，如實跳過：
   - **已掛載**：所屬 repo 在 `wtf-config/playbooks/mission-loop.md` 第 6 節雲端掛載清單內。
   - **資產可雲端**：任務範圍不依賴僅存本機 Drive 的大型二進位資產（圖片／影音／office 文件等未進 git_mirror 版控白名單的檔案）——純文字／程式碼改動即可完成。這筆速記若看得出要動素材（換圖、剪片、改文件排版），不提名。
   - **無阻塞**：不需等你當場決策、外部資料或本機資源即可動工。
   - **可增量**：切得成 ≤2 小時一塊；單一原子動作（如「報帳」「訂會議室」）不算，那是 B 類雜務，不會被判進這裡。
   - **低品味**：驗收可機檢（測試/read-back/斷言），不吃美感判斷。
   四條全中 → 在 `<WTF_ROOT>/missions/QUEUE.md`「提名」區塊加一行（狀態欄固定 `提名`，優先序 `—`，方向欄含掛載 repo 與中選理由的簡短括號註記，格式比照既有提名列）：
   `| <slug> | 提名 | — | <一句話方向>（掛載 <repo>；<四條命中摘要>） |`
   `<slug>` 用「YYYYMMDD-關鍵詞」；不覆蓋既有同 slug 行。**提名只是候選、棒子不碰**，需你另外把狀態改「待規劃」才會被夜間循環棒排入；當晚 19:00 提醒棒會照現有機制把提名清單一併推播給你確認。
   本步驟只 `git add missions/QUEUE.md`，commit push main（照第 2 節 3.5 分支制／night-pick 步驟 7 的重試規則）；與各專案 TaskLog 的 commit 分開跑，QUEUE.md 屬 WTF repo。

### B) 個人雜務（你自己執行、非專案：報帳/租車/繳費/預約…）
只進 App（owner=user）：
`source "<APP>/tools/env.sh"; python3 "<APP>/tools/todo-cli.py" add --project "個人事務" --title "<待辦>" --owner user --status todo`
不寫 TaskLog。

### C) 真判不出
只進 App：`... add --project "未分類" --title "<待辦>" --owner user --status todo`。

**重複速記**（與先前已收錄同名/同內容）→ 不重寫 TaskLog/App，僅執行移檔。
**移檔**：原檔 `<clippings>/` → `<ingested>/`（shell `mv`／`move`，路徑加引號）。

## 收尾

- **動到 TaskLog 的專案 repo**（各自）：**只 add 本次寫入的 TaskLog 檔**（勿 `add _context/` 或 `-A`，會掃進無關未追蹤檔）：
  `git -C "<path>" add "<本次 TaskLog 檔>" && git -C "<path>" commit -m "inbox: 語音待辦 N 筆"`，再 `git -C "<path>" push`。
  push 前若需同步先 `git -C "<path>" pull --rebase`；**工作區有既存未提交變更會擋 rebase → 跳過 pull 直接 push**；push 被拒才停下回報，不強推。
- **App 是即時雲端**，`todo-cli add` 當下已同步手機/桌機，無需 commit。

## 回報

每筆「檔名 → 類型（專案X：TaskLog＋App／個人：App／未分類）→ 結果」；重複而未重收；待補 github；各 repo commit/push 結果。

> 共用 skill，真相源 `wtf-config/skills/inbox/`。改後各機 `python wtf-config/sync_config.py sync` 重新部署。
