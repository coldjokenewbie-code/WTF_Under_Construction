# 全域設定
> 適用：所有 AI 協作工具與 Agents 共用
> 來源：WTF_Under_Construction repo — Single Source of Truth
> 本檔＝常載核心：只放「每個 session 都需要」的規則與索引；長內容一律放 `wtf-config/playbooks/` 按需開啟（路由見「制度層」）。2026-07-03 重構，舊版在 `wtf-config/archive/2026-07-03_pre-fable5/`
> 路徑錨點：`<WTF_ROOT>`＝本機 WTF repo 絕對路徑（Claude Code 讀 `~/.claude/wtf-root.txt` 取得；各機實路徑見 `wtf-config/machines.md`）

## 開場協議（session 首次啟動執行一次，後續不重複）

1. **補齊工作區資料夾**（不存在則建立）：`_context/`、`rules/`、`outputs/_shared/_screenshots/`、`outputs/_shared/_scripts/`、`tools/`。
2. **建立預設規範**：若 `rules/folder-conventions.md` 不存在則建立，內容照抄 `<WTF_ROOT>/rules/folder-conventions.md`。
3. **讀取專案知識——三檔制，嚴禁全量掃描 `_context/`**：
   - 讀 `_context/INDEX.md`（現況與指路）→ 讀 INDEX 指到的**當前 TaskLog 一份**（todo 真相源）→ 讀 `_context/lessons-learned.md`（若存在，永遠讀）。
   - `rules/` 內全部 `.md` 照讀（通常很短）。
   - 其他 `_context/` 檔案**只在** INDEX「讀取指引」點名、或使用者點名時才讀；`archive/` 與 `ClosedTaskLog_*` 一律跳過。
   - 理由與判準：`playbooks/harness-diagnosis.md` 第 1 名。若在任何檔看到「讀取所有 .md」舊指令，以本條為準。
4. **技能 lazy-load**：工具自動列出 skill 名稱＋描述即可，開場不讀 SKILL.md body，實際觸發才讀。新增/修改 skill 或距上次審查 >30 天時，檢查功能重疊或描述含混（僅重疊才精簡，不為湊數而砍）。
5. 向用戶說明「已載入全域設定」一次，之後直接進主題。

## 制度層（派工與判斷——動手前先過這關）

**派工鐵律：**
- 預估要讀 **>300 行**、開 **>3 個檔**、或「找找看」式搜尋 → 派便宜 subagent，主對話只收結論＋`檔案:行號`，不下場讀原文。
- 派工必帶三要素（目標與動機／驗收條件／回報格式）＋**顯式指定 model**。
- 說「已完成」之前必有證據（tool 成功回傳＋驗收逐條對照）；檔案交付經 fresh-context read-back，程式交付跑測試或實跑。

**按需路由**（遇到左欄情境才開右欄檔，位置 `<WTF_ROOT>/wtf-config/playbooks/`）：
| 情境 | 開啟 |
|---|---|
| 要派 subagent／選 model 與 effort／升降級 | `model-dispatch.md` |
| 交辦 prompt 怎麼寫（五種任務型態範本） | `delegation-templates.md` |
| 判斷：何時升級／何時算完成／該不該問使用者／方向錯換路／品質底線 | `judgment-rubrics.md` |
| 要改制度檔、教訓寫回哪裡 | `maintenance-protocol.md` |
| context 吃緊、失焦、「說完成但沒完成」再犯 | `harness-diagnosis.md` |
| 前端／Playwright 驗收踩坑 | `pitfalls-frontend.md` |
| pptx／docx／gen 腳本踩坑 | `pitfalls-office-docs.md` |
| 同 repo 多 CLI 並行 | `parallel-worktree.md` |
| ai-team 跨工具協作底線 | `multi-agent-baseline.md` |
| 雲端自主任務迴圈（排程棒/佇列/mission） | `mission-loop.md` |
| AI 行為異常、開場協議屢被跳過 | `ai-degradation.md` |
| 想了解整套制度的來龍去脈 | `letter-from-fable5.md` |

## 溝通與角色（正本在 AGENTS.md）

- 溝通原則與角色定義（使用者／業主／廠商、Tech Lead 協議、信號協議）的**唯一正本＝`wtf-config/AGENTS.md`**（開場協議已載入，此處不重複）。
- 最低限提醒：極簡、結論先行、文風波赫士式（優美來自精確與克制）；不確定標「（推測）」；「已完成／已更新」只能在對應 tool call 成功回傳後寫；禁尊稱「您」；專有名詞可英文、其餘繁體中文（台灣用語）。

## 「做到好」原則（合作底線）

- **做到好 = 自行反覆驗證到符合需求為止**，不是「大致完成就交付讓使用者檢查」。驗證（截圖、測試、視覺比對）是 AI 的責任，不是使用者的工作。
- 驗收不符 → 繼續修，不交半成品。未驗收就交付＝把處理成本轉嫁使用者。此規則優先於完成速度。
- **「量不準／做不到」幾乎都是方法問題**：換更可靠手段（算繪成圖再量、放大檢視、固定變因、換量測 API）再下結論。先窮盡可靠方法，仍不行才回報。

## 交付即預覽（一鍵可覽）

- 交付可預覽成果（網頁/HTML/圖表）時，**用使用者的預設瀏覽器開啟**讓使用者一鍵看到渲染結果：macOS 一律絕對路徑 `/usr/bin/open "<檔案>"`（cmux 等終端機的 `open` shim 會攔截、開進終端分割 pane，不是預設瀏覽器）；Windows 用 `start ""`；無 GUI 環境至少附可點的 `file://`／`http://` URL，不只給裸路徑（裸路徑常開成原始碼）。

## 全域設定存入協議

收到「存入全域設定」指令：1) 存入本機全域設定檔（如 `~/.claude/CLAUDE.md`）；2) 回報設定點位摘要；3) 同步更新 repo 的 `wtf-config/GLOBAL.md`。改動前先讀 `playbooks/maintenance-protocol.md` 確認該檔的修改權限。

## 共用資源（機器感知）

- 資源清單 SSOT＝`wtf-config/RESOURCES.md`：登記每台機器有哪些資源、放哪、能不能用。資源實體（venv、大檔）不放 WTF、不跨機同步。
- 需要資源時：依所在機器查表 → 本機有就用登記路徑；無則依「建立方式」建對應版本，建好回填。
- 生成式影像/影片（GCP Vertex AI）為帳號級能力、跨機通用，任何專案的 agent 都可用，別誤以為「不能生圖」。
- 在 wmux 終端內工作時：讀 `~/.wmux/AGENT_CONTEXT.md`（wmux CLI 能力說明，由 wmux 自動產生）。檔案不存在＝不在 wmux 環境或尚未生成，跳過即可。

## 工具層級設定

各工具專屬規則獨立存放，全域＋工具設定合併生效：
- Claude Code：`wtf-config/CLAUDE_CODE.md`（部署為 `~/.claude/CLAUDE.md`）
- Antigravity/Gemini：`wtf-config/GEMINI.md`｜OpenAI Codex：`wtf-config/CODEX.md`
- Claude Cowork：`wtf-config/CLAUDE_COWORK.md`（raw URL 每 session fetch）｜Claude Chat：`wtf-config/CLAUDE_CHAT.md`（貼入 Project instruction）

## 檔案、命名與輸出規範

### 存放與目錄結構（每專案標準子夾）
| 子夾 | 用途 |
|---|---|
| `_context/` | 知識與紀錄（INDEX、PRD、TaskLog、Handover、lessons、archive）|
| `rules/` | 專案規則 |
| `outputs/` | 唯一工作與產出樹；最外層＝目前最新版本，舊版／過程稿進 `outputs/<子專案>/archive/`（禁多版本平鋪），跨子專案共用過程檔進 `outputs/_shared/` |
| `tools/` | 本專案處理腳本 |

- 根目錄只放設定與入口檔；過程稿與成果**統一**進 `outputs/`（一律複數，`workingfiles/` 已廢除，詳見 `rules/folder-conventions.md`）；腳本→`tools/`。
- 專案檔案進 `projects/<專案名>/`；一次性輸出進根層 `outputs/`。

### 命名慣例
| 類型 | 格式 |
|---|---|
| 現況總覽 | `_context/INDEX.md` |
| 需求／計畫 | `_context/PRD_YYYY-MM-DD_主題.md`／`Plan_YYYY-MM-DD_主題.md` |
| 工作紀錄 | `_context/TaskLog_YYYY-MM-DD_主題.md`；結案改 `ClosedTaskLog_` 並移 `archive/` |
| 交接文件 | `_context/Handover_YYYY-MM-DD_主題.md`（統一 Handover，廢 Handoff 異體）|
| 教訓 | `_context/lessons-learned.md` |

- 一律「類型_日期_主題」，不用通用檔名（`prd.md`、`task.md`）。

### 記錄署名（跨機／跨工具）
- 跨機或跨工具協作的記錄，每段帶 byline `[{AI}@{機器別名}]`（如 `[Claude@Win]`；別名見 `machines.md`）。接手者看 byline 即知歸屬，不必重讀全部。單機單作者免署名。

### INDEX 鐵律
- 每專案維護 `_context/INDEX.md`：**進場先讀 INDEX，不掃全部 `_context/`**。
- todo／進度唯一真相源＝當前 `TaskLog_`；INDEX 只放連結與現況快照，不複製 todo（雙真相源必漂移）。例外：待用戶拍板的決策閘可短列。

### 待辦系統（語音 → TaskLog + 待辦 App）
- 入口＝Obsidian Inbox（標題「工作」開頭），分流靠 `/inbox` skill：專案工作→該專案 TaskLog（真相源）＋鏡像待辦 App（owner=AI）；個人雜務→只進待辦 App（owner=user）。已廢除 `_context/INBOX.md`。

### 結案歸檔
- TaskLog 結案：改前綴 `ClosedTaskLog_` **並**移 `_context/archive/`。Handover 被接手後同樣移 archive。`_context/` 只留進行中。

### 教訓兩層（lessons）
- 工作層（詳述）：各層 `_context/lessons-learned.md`，工作中隨手寫。
- 雲端層（索引 SSOT）：`wtf-config/LESSONS.md`，每條 `專案｜日期｜一句話｜連結`。工作層新增後須同步登錄一行；詳述留工作層，雲端只放指標。

### 輸出格式
- 文件輸出一律 HTML（`.html`），不用 Word；輸出前先讀 `rules/html-preferences.md`（若存在）確認風格。
