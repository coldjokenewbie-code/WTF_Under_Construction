# 全域設定（GLOBAL）

> **全域設定**＝本檔（通則）＋`AGENTS.md`（溝通與角色），所有 AI 開場必讀；跨機、CLI、Cowork、Chat 共用單一真相源。
> **來源**：WTF_Under_Construction。`<WTF_ROOT>` 由本工具的 `wtf-root.txt` 取得（Claude：`~/.claude/wtf-root.txt`），各機路徑見 `machines.md`。
> **維護**：本檔常駐，長細則按需讀 `playbooks/`；改前必讀 `playbooks/maintenance-protocol.md`。

## 開場協議（session 首次啟動執行一次，後續不重複）

1. **補齊工作區資料夾**（不存在則建立）：`_context/`、`rules/`、`workingfiles/outputs/_shared/_screenshots/`、`workingfiles/outputs/_shared/_scripts/`、`tools/`。
2. **建立預設規範**：若 `rules/folder-conventions.md` 不存在，照抄 `<WTF_ROOT>/rules/folder-conventions.md` 建立。
3. **讀取專案知識——三檔制，嚴禁全量掃描 `_context/`**：
   - 讀 `_context/INDEX.md`（現況與指路）→ 讀 INDEX 指到的**當前 TaskLog 一份**（待辦真相源）→ 讀 `_context/lessons-learned.md`（若存在，永遠讀）。
   - `rules/` 內全部 `.md` 照讀（通常很短）。
   - 其他 `_context/` 檔案**只在** INDEX「讀取指引」點名、或使用者點名時才讀；`archive/` 與 `ClosedTaskLog_*` 一律跳過。
   - 若在任何舊檔看到「讀取所有 .md」指令，以本條為準。
4. **技能載入**：照 AGENTS.md「Skills 載入協議」（lazy-load，開場不讀 body）。
5. 向用戶說明「已載入全域設定」一次，之後直接進主題。

## 派工與判斷（動手前先過這關）

**派工鐵律（風險／獨立性判斷，工具中立）：**
- **適合派工**：工作可獨立完成、讀取密集、中間過程會產生大量污染主 context 的輸出、可平行處理（如「找找看」式搜尋、大範圍讀取後摘要）→ 派給適合的執行 agent，主對話只收結論＋`檔案:行號`，不下場讀原文。
- **不適合派工**：修改彼此高度耦合、多人/多 agent 同時動同一區域、協調成本高於直接執行的成本 → 主 agent 自行處理較划算。
- **分流先於執行（2026-09-17 PO 裁定）**：收到任務先評估是否需要高階模型。不需要，低階直接完成；需要，高階只做策劃、拆解、驗收，執行交低階。驗收標準不變的前提下，Token CP 值優先；低階做不來就升級，不硬做。每次派工紀錄寫明模型階層與理由。工具對應：Claude haiku／sonnet／opus；Codex reasoning low／medium／high；Antigravity 依可選模型。
- 派工必帶三要素：目標與動機、驗收條件、回報格式。各工具依模型調度規則選執行者（Claude 見 `model-dispatch.md`；其他工具依自身轉接層）；本層按風險與獨立性決定是否派工，模型層再考量額度，不降低驗收標準。
- 說「已完成」之前必有證據：tool 成功回傳＋驗收逐條對照。**高風險或跨模型的成果**：fresh-context 或跨工具獨立驗證；**低風險單點修改**：允許主 agent 自行執行命令與 read-back，不強制每次另派 agent；**ai-team 仍一律由非作者輪流驗收**。檔案交付要經 fresh-context read-back；程式交付要跑測試或實跑。

**按需路由**（遇到左欄情境才開右欄檔，位置 `<WTF_ROOT>/wtf-config/playbooks/`）：

| 情境 | 開啟 |
|---|---|
| 要派 subagent／選 model 與 effort／升降級 | `model-dispatch.md` |
| 交辦 prompt 怎麼寫（五種任務型態範本） | `delegation-templates.md` |
| 判斷：何時升級／何時算完成／該不該問使用者／方向錯換路／品質底線 | `judgment-rubrics.md` |
| 引用統計數據、畫數據圖表、跨年或同期比較、多來源數字打架 | `data-citation.md` |
| 決定讀寫位置、啟動服務、git／commit／push | `git-mirror.md` |
| 交付預覽、可存檔程式／網頁、匯報格式 | `delivery-conventions.md` |
| 要改制度檔、教訓寫回哪裡 | `maintenance-protocol.md` |
| context 吃緊、失焦、「說完成但沒完成」再犯 | `harness-diagnosis.md` |
| 前端／Playwright 驗收踩雷 | `pitfalls-frontend.md` |
| pptx／docx／gen 腳本踩雷、Excel／CSV 匯出 | `pitfalls-office-docs.md` |
| 同 repo 多 CLI 並行 | `parallel-worktree.md` |
| ai-team 跨工具協作底線 | `multi-agent-baseline.md` |
| 雲端自主任務迴圈（排程棒/佇列/mission） | `mission-loop.md` |
| AI 行為異常、開場協議屢被跳過 | `ai-degradation.md` |
| 想了解整套制度的來龍去脈 | `letter-from-fable5.md` |

**工作位置／版控**：決定任何讀寫位置、啟動服務，或遇到 git／推／commit／push 前，先查 `projects-registry.md` 與 `playbooks/git-mirror.md`。所有專案 Drive 工作、git_mirror 版控；**唯一例外 WTF_Under_Construction 本體直接在 git_mirror**。Drive 禁原地 git；Git_work／git_work_bk 與未登錄路徑禁用。

## 工作品質底線

- **做到好＝自行反覆驗證到符合需求為止**，不是「大致完成就交給使用者檢查」。驗證（截圖、測試、視覺比對）是 AI 的責任。
- 驗收不符 → 繼續修，不交半成品。未驗收就交付＝把處理成本轉嫁給使用者。此規則優先於完成速度。
- **引用統計數值／比較／畫圖前**：必標起訖期間與口徑；不得補參數，同期同口徑才能比較，查不到即標未取得並排除。先讀 `playbooks/data-citation.md`。
- **「量不準／做不到」幾乎都是方法問題**：換更可靠的手段（先算繪成圖再量、放大檢視、固定變因、換量測 API）再下結論。窮盡可靠方法仍不行，才回報做不到。
- **交付可看可聽成品**：主動背景預覽；macOS 用 `/usr/bin/open -g`，影音只顯示所在位置、不自動播放，批次開資料夾；命令與例外見 `playbooks/delivery-conventions.md`。
- **可存檔程式／網頁**：預設指向目標資料夾，記住首次選擇以後寫回；不能精確預設就明示路徑，禁以 Documents 等系統資料夾保底。檢核頁覆蓋原檔；細則先讀 `playbooks/delivery-conventions.md`，FSA 實作再讀 `playbooks/pitfalls-frontend.md`。
- 溝通方式與角色分工的全部規則在 `AGENTS.md`（兩檔綁定必讀，本檔不重複）。

## 全域設定的維護

- **改制度或存入全域設定前**：先讀 `playbooks/maintenance-protocol.md`；更新對應 SSOT，跑 `sync_config.py sync` 後核對 `check`，再回報點位。工具入口映射與完整存入協議見該檔。
- **需要環境／API／大檔資源**：查 `RESOURCES.md` 本機列；wmux 環境另讀 `~/.wmux/AGENT_CONTEXT.md`（不存在略過）。

## 檔案、命名與輸出規範

**每專案標準子資料夾：**

| 子夾 | 用途 |
|---|---|
| `_context/` | 知識與紀錄（INDEX、PRD、TaskLog、Handover、lessons、archive）|
| `rules/` | 專案規則 |
| `workingfiles/` | 唯一工作與產出樹（過程稿＋定案產出皆在此，見下方內部規則）|
| `tools/` | 本專案處理腳本 |

- 根目錄只放設定與入口檔；所有作業與產出一律在 `workingfiles/` 內進行；腳本進 `tools/`。專案檔案進 `projects/<專案名>/`。
- `workingfiles/` 內部規則：草稿、半成品、中間產物直接放 `workingfiles/` 下（正式定案前都留在這裡）；定案交付物移入 `workingfiles/outputs/`（一律複數）——最外層＝目前最新版本，舊版進 `workingfiles/outputs/<子專案>/archive/`（禁止多版本平鋪）；跨子專案共用過程檔進 `workingfiles/outputs/_shared/`。
- Drive 端出現非 `.retired-` 結尾的 `.git` 視為異常，回報並停用（見 `playbooks/git-mirror.md`）。

**命名慣例**（一律「類型_日期_主題」，不用通用檔名如 `prd.md`、`task.md`）：

| 類型 | 格式 |
|---|---|
| 現況總覽 | `_context/INDEX.md` |
| 需求／計畫 | `_context/PRD_YYYY-MM-DD_主題.md`／`Plan_YYYY-MM-DD_主題.md` |
| 工作紀錄 | `_context/TaskLog_YYYY-MM-DD_主題.md`；結案改前綴 `ClosedTaskLog_` 並移入 `archive/` |
| 交接文件 | `_context/Handover_YYYY-MM-DD_主題.md`（統一用 Handover，廢除 Handoff 寫法）|
| 教訓 | `_context/lessons-learned.md` |

- **INDEX 鐵律**：每專案維護 `_context/INDEX.md`，進場先讀 INDEX、不掃全部 `_context/`。待辦與進度的唯一真相源＝當前 TaskLog；INDEX 只放連結與現況快照，不複製待辦內容（兩處真相必然漂移）。例外：等使用者拍板的決策點可短列。
- **記錄署名**：跨機器或跨工具協作的紀錄，每段帶署名 `[{AI}@{機器別名}]`（如 `[Claude@Win]`；別名見 `machines.md`），接手的人一眼看出誰寫的。單機單作者免署名。
- **待辦系統**：入口＝Obsidian Inbox（標題「工作」開頭的速記），用 `/inbox` skill 分流——專案工作→該專案 TaskLog（真相源）＋鏡像到待辦 App（owner=AI）；個人雜務→只進待辦 App（owner=user）。`_context/INBOX.md` 已廢除，看到即視為過時檔。
- **結案歸檔**：TaskLog 結案＝改前綴 `ClosedTaskLog_` **並**移入 `_context/archive/`；Handover 被接手後同樣歸檔。`_context/` 只留進行中的檔案。
- **教訓兩層**：工作層（詳述）寫各專案 `_context/lessons-learned.md`；雲端層（索引）在 `wtf-config/LESSONS.md`，每條格式「專案｜日期｜一句話｜連結」。工作層新增後須同步登錄索引一行。
- **共編檔鐵律（`W_` 前綴，2026-08-14 PO 裁定）**：檔名以 `W_` 開頭的文件＝使用者與 AI 共編，預設使用者可能已直接編輯。使用者說「我已編輯」後：**禁止用產生器／整檔重建腳本改檔**（會覆蓋使用者編輯）；動檔前必先重新讀取檔案最新內容（以 Drive 最新存檔版為基準），之後只做就地增量修改，改前備份至 archive。
- **Excel／CSV 輸出**：先讀 `playbooks/pitfalls-office-docs.md`（含 xlsx 字體及匯出規範）。
- **選擇匯報／交付格式**：PO 匯報優先 HTML（有 `rules/html-preferences.md` 須先讀）；業主／廠商正式交付依專案格式。見 `playbooks/delivery-conventions.md`。
