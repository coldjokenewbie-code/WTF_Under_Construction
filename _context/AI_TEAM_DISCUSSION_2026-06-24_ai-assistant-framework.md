# AI Team 討論：AI 中立的自主任務助理框架
> Tech Lead：Claude@comaMacBookAir（macOS）
> 開始：2026-06-24
> 通道：同機 headless CLI 直驅（codex / agy）；agy 若空輸出（非 TTY）→ 非同步落檔討論

## 需求（PO）
打造一個 AI 助理框架：
- **AI 中立**：不綁定特定 AI（Claude / Codex / Gemini 可互換）
- **自主執行**：少人工介入即完成任務
- **省 API**：避免不必要的 API 額度消耗
- **低風險**：避免網站操作、破壞性指令、資料外送

產出：3 個規劃/製作方案 + 挑一個工作實作測試。

## 使用者工作型態（grounding）
互動式 HTML 導覽頁(kiosk/mobile)、文件對位(PPT/docx/PDF 轉檔渲染量測)、儀表板、Remotion 影片、跨機設定同步、PM/todo app。
已有基礎：WTF SSOT（hook 自動同步、skills、AGENT_SIGNAL 信號協議、sync_config.py、projects-registry）。

---

## Round 1 — 各 agent 初版方案

### [Codex@Mac] Round 1
- **定調**：本地 Orchestrator + Adapter + Policy Gate。核心決策/掃描/轉檔/量測/同步全本地確定性腳本；LLM 只做模糊判斷、規劃、文字生成、例外修復。
- 組件：Task Orchestrator（狀態機）、Tool Registry（Playwright/LibreOffice/ffmpeg/Remotion/PDF/git/sync_config）、AI Adapter（`plan()/judge()/summarize()/repair()` 統一介面，底層可換）、Policy Gate（攔網站操作/刪檔/git reset/外送/API）、Artifact Store、Signal Bus（擴 `REQUEST/DONE/VERIFIED/BLOCKED/NEED_APPROVAL`）。
- AI 中立：Adapter 只收標準 JSON（context/goal/constraints/available_tools/expected_output）；LLM 只回 structured action proposal，不直接碰檔案/網站；各 AI 只是行為引擎，不持有真相源。
- 風險緩解：先用規則/檔名/MIME/diff 分類，低信心才呼叫 LLM（省成本）；高風險動作只發 `NEED_APPROVAL`、外送先 redaction+allowlist（安全）；內部只認自訂 JSON protocol（中立）。

### [Antigravity@Mac] Round 1
- **定調**：「Spec-driven Deterministic Loop」。任務狀態/測試案例/操作限制以中立 Spec(MD/JSON) 定義；LLM 只做代碼修改與推理，流程控制/執行驗證/安全攔截全由本地腳本主導。
- 組件：Task Broker（解析 Spec、狀態管理）、Protocol Adapter（統一吃 AGENT_SPEC.md、用 TaskLog + AGENT_SIGNAL 通訊）、Local Validator（本地跑測試/Playwright 截圖，文字回饋，不讓 AI 通靈驗收）。
- AI 中立：不用 AI 特有 API/plugin，只需 AI 有「讀寫檔 + 跑 CLI」能力；高級操作封裝成本地 CLI。
- 風險緩解：**最大嘗試次數(如 3)+冷卻**防 try-error 燒額度；本地 AST 安全過濾器擋 `rm -rf`/外送、限制寫入目錄；低階模型連敗 2 次自動升級或降為純代碼生成。

### [Claude@Mac] Round 1 綜整
三方高度收斂，共識骨架：**本地確定性核心 + 薄 AI Adapter（中立）+ Policy/安全閘 + 重試上限**。差異僅措辭。
**PO 追加需求（Round 1 後）：框架必須能「自動學習」**——納入 Round 2 深化。

---

## Round 2 — 自動學習迴圈（三方再收斂）

### [Codex@Mac] Round 2
- 四段式：**事件紀錄 → 蒸餾 → 審核 → 啟用**。學的是可重用「決策規則/失敗模式/修復步驟/任務模板/可腳本化流程」，非完整對話。
- 三層存放：執行 log（本地事件）→ 專案 `lessons-learned.md` → 跨專案穩定規則進 `wtf-config/LESSONS.md`（全域只建議、人工審核才升級）。
- 升級管線：一次性 LLM 解法重複 2-3 次 → checklist → script → skill；啟用前最小測試（固定輸入同輸出/拒危險輸入/能回報不確定）；通過後加入「本地優先路由」。
- 防呆：lesson 須帶 scope/來源 commit/適用條件/反例/驗證；衝突不自動合併。學習省成本：優先本地規則蒸餾，只在多案例聚類/規則衝突才呼叫 LLM；nightly 設 token budget、只讀 diff 摘要+metadata、低價模型分類。
- 指標：`llm_calls_per_task`↓、`local_resolution_rate`↑、`repeat_task_cost_delta`、`script_promotion_rate`、`regression_rate`、`policy_block_rate`、`lesson_hit_success_rate`。

### [Antigravity@Mac] Round 2
- 學「環境/邊界知識 + 確定性工作流」。專案層寫 `lessons-learned.md` + `tools/` 腳本；全域進 `wtf-config/LESSONS.md`，高頻通用升 `wtf-config/skills/`。
- 回饋兩路：**開場注入**（依 goal 檢索 lessons 注入 adapter 防重蹈）+ **命中即直接跑本地腳本繞過 LLM**。
- 升級：失敗→輕量 AI 做 RCA 寫 lesson；成功且歷經 2+ 次 LLM 互動→觸發蒸餾→封裝成帶參數腳本入 `tools/`→註冊 Trigger Rules。
- 防呆：AI 生成的 lesson/script 預設 `.draft`，**PO 於 session-end/nightly 人工核准才生效**；新腳本首跑須過 AST + Policy Gate 沙盒。學習省 API：禁對話中即時整理，延遲到 session-end/nightly 批次；模型分級（Flash/Haiku 做 RCA，Opus/Pro 才做 codegen）。
- 指標：LLM Call Rate↓（指數）、Deterministic Ratio↑（高頻>80%）、API Cost per Task↓；記 `session-logs/` 由 sync_config 上 dashboard 出「複利曲線」。

### [Claude@Mac] Round 2 綜整
學習迴圈共識：**結構化事件 log → 批次蒸餾（延遲到 session-end/nightly、用便宜模型）→ draft 草案 → PO/policy 審核 → 升級成 script/skill → 本地優先路由（命中即繞過 LLM）**。與 WTF 既有兩層 lessons + nightly「只建議不自改」+ nightly-notify 核准機制天然契合。複利＝越用越多任務被本地化，LLM 呼叫率指數下降。

---

## Round 3 — 鎖定共識 + 三方案框定 + PoC 選擇
（Tech Lead 將收斂結果收斂成「3 個建置層級方案」供 PO 選，並挑 PoC，請兩 agent 挑毛病）

### [Codex@Mac] Round 3
- Blind spots：① Spec 格式未鎖（JSON/MD 並存難驗）→ 先定最小 JSON schema；② Tool Registry 缺版本與 I/O 契約 → 難回滾；③ Policy Gate 只列禁止項不夠 → 要「允許清單 + dry-run」。
- Must-fix：① 先定 `task_spec.schema.json`、`event.schema.json`、artifact 輸出格式；② Policy Gate 包「命令建構前 + 執行前」兩層，handler 只能透過受控 executor 跑 shell。
- Verify：命中 handler 時 `llm_calls=0` 且未呼叫 adapter／事件含 start+policy+handler_result+artifact+finish／`rm -rf`+網路+`git push`+白名單外寫入皆被拒並記錄／掃描只唯讀 git log／learn 產 draft 不直接升級。

### [Antigravity@Mac] Round 3
- Blind spots：① Fallback 狀態丟失（退回 LLM 會重做已完成步驟）；② 靜態 Registry 難處理動態參數；③ learn.py 只靠 metrics、缺 error trace 難產實質升級草案。
- Must-fix：① 禁 `subprocess.run(shell=True)` + 對 registry 掃出路徑做白名單防穿越/注入；② 定 Fallback Payload 規格（把 handler 執行軌跡+失敗原因打包給 adapter）。
- Verify：斷網/mock 下 `llm_calls=0` 且出正確 HTML／`rm -rf` 任務被拒寫 `BLOCKED`／Adapter 抽換無痛／注入字元(`;` `..`)被過濾／events.jsonl 完整生命週期。

### [Claude@Mac] Round 3 — 共識鎖定（CONSENSUS）
3 輪達成共識，進入實作。**全數 Must-Fix 納入**：
1. 鎖定 `schemas/task_spec.schema.json`、`schemas/event.schema.json`、HTML artifact 格式。
2. Policy Gate 雙層（`check_command` 建構前 + `executor.run` 執行前重檢）+ 寫入目錄白名單 + denylist（網路/破壞/push）+ dry-run。
3. 禁 `shell=True`，只走受控 executor（argv list）；registry 路徑 resolve + 反穿越（拒 `..`、限已登記絕對路徑）。
4. Fallback Payload 協議：`{goal, context, handler_trace, failure_reason, constraints}` 打包給 adapter；adapter 預設 dry（不花 API），`--allow-llm` 才真呼叫且仍過 policy。
5. learn.py 兼收 metrics + 失敗 trace；偵測重複 fallback → 產 `.draft` 升級草案，不自動生效（PO 審核）。

**交付給 PO 的 3 方案**：A 就地擴充 WTF（最省，半自動）／**B 獨立本地 Orchestrator（推薦，本次實作 MVP）**／C 全自動 daemon（最自主，成本最高）。

---

## 實作 + 輪流驗收紀錄

### BUILD（Claude 主筆，方案 B MVP）
位置 `tools/assistant/`（889 行 Python，零外部依賴）。組件：Orchestrator(`run_task.py`)、Policy Gate 雙層(`policy.py`)、受控 executor(`executor.py`)、registry(版本+I/O契約)、AI 中立 adapter(claude/codex/agy，dry 預設不花 API)、事件 log(schema 驗證)、學習器(`learn.py`)、2 個確定性 handler(project_digest / config_sync_check)、JSON Schema(task_spec/event)、自驗套件(`tests/test_safety.py`)。

實測：project_digest 掃 10 repo 出 13 區 HTML、llm_calls=0；config_sync ok；未命中任務走 fallback dry(llm_calls=0)；learn.py runs=6、**llm_calls_per_task=0.0**、local_resolution_rate=0.667、偵測 summarize_pdf 重複 fallback→自動產升級草案 .draft。自驗最終 **30/30 全過**。

自修 bug：① git format `|` 被 policy 當注入擋（證明 policy 有效）→改 0x1f；② handler=None 違反 schema→events 過濾 None。

### VERIFY（輪流驗收，Round 4）
- [Codex@Mac]：**PASS with notes**，12/12 checklist 過。建議補：壓力/超時測試、schema 版本相容測試、adapter 非 dry 的 mock 隔離測試（皆列未來工作，非安全洞）。
- [Antigravity@Mac]：**PASS with notes**，5/5 過，抓 3 個真實安全洞：① 寫入區 write-then-execute；② git clone/pull/fetch 網路未擋；③ symlink/別名改名繞過 denylist。
- [Claude@Mac] 修補：① policy 禁執行/直譯 data|outputs 內檔案；② git 網路子命令 allow_network=False 時拒（全 token 集合比對，修掉 `git -C <dir> pull` 漏網）；③ realpath 真實 basename 再比黑名單。加 6 項回歸測試→ **30/30**。
- [Antigravity@Mac] 收尾複驗：**CLOSED-PASS**。

### 結論
3 輪討論 + 1 輪輪流驗收（含修補+複驗）完成。交付 PO：`outputs/AI助理框架_方案與實作_2026-06-24.html`（3 方案 + B MVP 實作 + 證據）。**待 PO 最終驗收後才 commit**（ai-team 鐵則：不自行 commit）。



