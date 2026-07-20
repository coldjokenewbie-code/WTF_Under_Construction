# 全域設定（GLOBAL）

> **定義**：「全域設定」＝本檔＋`AGENTS.md` 兩檔，所有 AI 開場必讀，內容互不重複——通則與規範在本檔，溝通方式與角色分工在 AGENTS.md。
> **應用範疇**：一切 AI 介面通用——CLI agent（Claude Code、Antigravity、Codex）、Claude Cowork、Claude Chat。
> **目的**：讓任何 AI 在任何機器、任何介面上，用同一套規則工作；規則只寫一次（Single Source of Truth），改一處全體生效。
> **來源**：WTF_Under_Construction repo。`<WTF_ROOT>`＝本機 WTF repo 絕對路徑（Claude Code 讀 `~/.claude/wtf-root.txt` 取得；各機實路徑見 `wtf-config/machines.md`）。
> **維護**：本檔每個 session 都會載入，只放每次都需要的規則；長內容一律放 `wtf-config/playbooks/`，遇到情境才開（路由表見下）。改本檔前先讀 `playbooks/maintenance-protocol.md`。

## 開場協議（session 首次啟動執行一次，後續不重複）

1. **補齊工作區資料夾**（不存在則建立）：`_context/`、`rules/`、`outputs/_shared/_screenshots/`、`outputs/_shared/_scripts/`、`tools/`。
2. **建立預設規範**：若 `rules/folder-conventions.md` 不存在，照抄 `<WTF_ROOT>/rules/folder-conventions.md` 建立。
3. **讀取專案知識——三檔制，嚴禁全量掃描 `_context/`**：
   - 讀 `_context/INDEX.md`（現況與指路）→ 讀 INDEX 指到的**當前 TaskLog 一份**（待辦真相源）→ 讀 `_context/lessons-learned.md`（若存在，永遠讀）。
   - `rules/` 內全部 `.md` 照讀（通常很短）。
   - 其他 `_context/` 檔案**只在** INDEX「讀取指引」點名、或使用者點名時才讀；`archive/` 與 `ClosedTaskLog_*` 一律跳過。
   - 若在任何舊檔看到「讀取所有 .md」指令，以本條為準（判準見 `playbooks/harness-diagnosis.md`）。
4. **技能載入**：照 AGENTS.md「Skills 載入協議」（lazy-load，開場不讀 body）。
5. 向用戶說明「已載入全域設定」一次，之後直接進主題。

## 派工與判斷（動手前先過這關）

**派工鐵律：**
- 預估要讀超過 300 行、開超過 3 個檔、或做「找找看」式搜尋 → 派便宜 subagent 處理，主對話只收結論＋`檔案:行號`，不下場讀原文。
- 派工必帶三要素：目標與動機、驗收條件、回報格式；並**顯式指定 model**。
- 說「已完成」之前必有證據：tool 成功回傳＋驗收逐條對照。檔案交付要經 fresh-context read-back；程式交付要跑測試或實跑。

**按需路由**（遇到左欄情境才開右欄檔，位置 `<WTF_ROOT>/wtf-config/playbooks/`）：

| 情境 | 開啟 |
|---|---|
| 要派 subagent／選 model 與 effort／升降級 | `model-dispatch.md` |
| 交辦 prompt 怎麼寫（五種任務型態範本） | `delegation-templates.md` |
| 判斷：何時升級／何時算完成／該不該問使用者／方向錯換路／品質底線 | `judgment-rubrics.md` |
| 要改制度檔、教訓寫回哪裡 | `maintenance-protocol.md` |
| context 吃緊、失焦、「說完成但沒完成」再犯 | `harness-diagnosis.md` |
| 前端／Playwright 驗收踩雷 | `pitfalls-frontend.md` |
| pptx／docx／gen 腳本踩雷 | `pitfalls-office-docs.md` |
| 同 repo 多 CLI 並行 | `parallel-worktree.md` |
| ai-team 跨工具協作底線 | `multi-agent-baseline.md` |
| 雲端自主任務迴圈（排程棒/佇列/mission） | `mission-loop.md` |
| AI 行為異常、開場協議屢被跳過 | `ai-degradation.md` |
| 想了解整套制度的來龍去脈 | `letter-from-fable5.md` |

**Claude_cowork 專案版控鐵律**（只要出現「git」「推」「commit」「push」等字眼，或要決定「在哪個資料夾讀寫檔案、啟動服務」，一律先查此規則）：
- **所有專案一律「Drive 工作＋git_mirror 鏡像版控」，不存在「純程式 repo」分類**；唯一例外＝WTF_Under_Construction（控管架構 repo＝所有專案的原則與系統架構，本體直接在 `git_mirror/`）。舊 `Git_work`／`git_work_bk` 資料夾已禁用，registry 未登記的路徑不得當工作位置（PO 2026-07-20 裁定）。
- Drive 內任何專案，一律不得原地 git（`init`/`add`/`commit`/`push` 皆禁）——git 與 Drive 同步會互相衝突、鎖檔（已有先例）。
- 查本機是否存在 `git_mirror/<專案名>/`（Mac＝`/Users/coma/git_mirror/`，Windows＝`E:\git_mirror\`；不隨 Drive 同步，各機獨立）：
  - 存在 → **Drive 為唯一真相源，工作在 Drive 做**；`git_mirror/` 只是版控出口。
  - 不存在 → 查 GitHub remote（見 `projects-registry.md`）：有就 clone 到 `git_mirror/<專案名>/`；沒有就在該處建新 repo。都不碰 Drive 端。
- **使用者說「推上 git」＝一整套動作的簡稱，不是字面指令**：
  - 推送前（Drive→mirror）：依副檔名白名單（html/css/js/json/md/ts/tsx/jsx/mjs/py/txt/yaml/yml/sh）複製 Drive→mirror（單向覆蓋，含 `_context/*.md`，不是只有程式碼），再從 mirror `commit`＋`push`。大型二進位（docx/pptx/pdf/圖片/影片）不複製，留在 Drive。
  - 開工前（mirror→Drive，反向對稱）：先在 mirror `git pull`（拉其他機器已推的新 commit），再依同一白名單複製 mirror→Drive，才開始在 Drive 讀改檔案——避免改在別人已推過的舊版本上。
- **複製後必核**：對照 Drive 與 mirror 的 `_context/` 檔案清單一致；缺檔＝漏複製，不是「這次沒改」。
- **後果提醒**：鏡像不全＝工作紀錄只存單機、未進版控＝遺失風險。

## 工作品質底線

- **做到好＝自行反覆驗證到符合需求為止**，不是「大致完成就交給使用者檢查」。驗證（截圖、測試、視覺比對）是 AI 的責任。
- 驗收不符 → 繼續修，不交半成品。未驗收就交付＝把處理成本轉嫁給使用者。此規則優先於完成速度。
- **「量不準／做不到」幾乎都是方法問題**：換更可靠的手段（先算繪成圖再量、放大檢視、固定變因、換量測 API）再下結論。窮盡可靠方法仍不行，才回報做不到。
- **交付即預覽**：交付可預覽成果（網頁/HTML/圖表）時，主動用使用者的預設瀏覽器開啟。macOS 一律用絕對路徑 `/usr/bin/open "<檔案>"`（終端機如 cmux 會攔截裸 `open` 開進終端分割視窗）；Windows 用 `start ""`；無 GUI 環境至少附可點的 `file://`／`http://` 連結，不能只給裸路徑。
- 溝通方式與角色分工的全部規則在 `AGENTS.md`（兩檔綁定必讀，本檔不重複）。

## 全域設定的維護

- **存入協議**：收到「存入全域設定」指令時——1) 更新 repo 的 `wtf-config/GLOBAL.md` 或對應工具檔；2) 跑 `sync_config.py sync` 部署到本機；3) 回報設定點位摘要。改動前先讀 `playbooks/maintenance-protocol.md` 確認該檔的修改權限。
- **工具層級設定**（各工具專屬差異，與全域設定合併生效）：
  - Claude Code：`wtf-config/CLAUDE_CODE.md`（部署為 `~/.claude/CLAUDE.md`）
  - Antigravity/Gemini：`wtf-config/GEMINI.md`｜OpenAI Codex：`wtf-config/CODEX.md`
  - Claude Cowork：`wtf-config/CLAUDE_COWORK.md`（每 session 以 raw URL 抓取）｜Claude Chat：`wtf-config/CLAUDE_CHAT.md`（貼入 Project instruction）
- **共用資源**：清單 SSOT＝`wtf-config/RESOURCES.md`，登記每台機器有哪些資源（venv、大檔、API 能力）、放哪、能不能用。需要時依所在機器查表；本機沒有就照「建立方式」建好並回填。生成式影像/影片（GCP Vertex AI）是帳號級能力、跨機通用。在 wmux 終端內工作時讀 `~/.wmux/AGENT_CONTEXT.md`（不存在＝不在 wmux 環境，跳過）。

## 檔案、命名與輸出規範

**每專案標準子資料夾：**

| 子夾 | 用途 |
|---|---|
| `_context/` | 知識與紀錄（INDEX、PRD、TaskLog、Handover、lessons、archive）|
| `rules/` | 專案規則 |
| `outputs/` | 唯一工作與產出樹；最外層＝目前最新版本，舊版與過程稿進 `outputs/<子專案>/archive/`（禁止多版本平鋪）；跨子專案共用過程檔進 `outputs/_shared/` |
| `tools/` | 本專案處理腳本 |

- 根目錄只放設定與入口檔；過程稿與成果統一進 `outputs/`（一律複數；`workingfiles/` 已廢除）；腳本進 `tools/`。專案檔案進 `projects/<專案名>/`；一次性輸出進根層 `outputs/`。
- Drive 端出現非 `.retired-` 結尾的 `.git` 視為異常，回報並停用（版控規則見上方「版控鐵律」）。

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
- **輸出格式**：文件輸出一律 HTML（`.html`），不用 Word；輸出前若存在 `rules/html-preferences.md` 先讀完再動筆。
