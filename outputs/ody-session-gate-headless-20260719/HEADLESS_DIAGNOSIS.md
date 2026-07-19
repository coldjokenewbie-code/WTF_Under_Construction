# Session gate headless 診斷

> ody 契約：`wtf-session-gate-headless-20260719`  
> 環境：macOS、Claude Code 2.1.215（歷史 project canary 為 2.1.210）  
> 結論：原假說「headless 不展開 user 層 import」被第一手事件反證。故障主因是正式 import 只寫入部署副本 `~/.claude/CLAUDE.md`，未寫入 SSOT `wtf-config/CLAUDE_CODE.md`；後續同步使部署副本回復成無 import 的 SSOT 內容。  
> 驗收狀態：本文件未經獨立複驗，不宣稱 ody PASS。

## 實測矩陣

標記：**實測**＝有 Claude Code 原始事件或 transcript；**未實測**＝沒有足夠第一手資料；**推論**＝由已觀察事實推導。

| 模式 | import 來源 | `include` | `file_path` | `parent_file_path` | 判定 |
|---|---|---:|---|---|---|
| 互動 | user | — | — | — | 依任務要求跳過 |
| headless | user only | 有，2 筆 | 正式 bundle 的 `AGENTS.md`、`GLOBAL.md` | `/Users/coma/.claude/CLAUDE.md` | **實測**；session `f96bc555…`，`memory_type=User` |
| headless | project only | 有，2 筆 | canary 專案內 `wtf-bundle/GLOBAL.md`、`AGENTS.md` | canary 專案的 `CLAUDE.md` | **實測**；另有本體 `session_start` 事件 |
| headless | user + project | 未完成 | — | — | **未實測**；本次執行時 `claude auth status` 為 `loggedIn:false`，hook 在認證失敗前未啟動 |

### user only 原始事件

完整副本：`evidence_user_headless.events.jsonl`。原檔仍在 phase 4 scratchpad：`gate-canary/logs/phase4/il.jsonl`。

```json
{"file_path":"/Users/coma/.claude/wtf-session-bundles/ba55340b…/AGENTS.md","memory_type":"User","load_reason":"include","parent_file_path":"/Users/coma/.claude/CLAUDE.md"}
{"file_path":"/Users/coma/.claude/wtf-session-bundles/ba55340b…/GLOBAL.md","memory_type":"User","load_reason":"include","parent_file_path":"/Users/coma/.claude/CLAUDE.md"}
```

同一 session transcript 的模型正確回答 14 種副檔名白名單，證明內容不只發事件，也進入模型 context。這直接否定「`claude -p` 不展開 user 層 `@import`」。

### project only 原始事件

完整摘錄副本：`evidence_project_headless.events.jsonl`。來源為 2026-07-16 canary transcript 的 recorder 輸出。

```text
include .../proj/wtf-bundle/GLOBAL.md | parent: .../proj/CLAUDE.md
include .../proj/wtf-bundle/AGENTS.md | parent: .../proj/CLAUDE.md
session_start .../proj/CLAUDE.md | parent: null
```

此案例把 bundle 複製進專案，再用相對 import。先前「專案外絕對路徑 import」測項未載入，不能把 project only 的結果外推到任意外部路徑。

### 本次重跑限制

本次建立 `recorder-settings.json` 與三組隔離 fixture，實際呼叫 `claude -p`；CLI 在模型呼叫前回傳 `Not logged in`，沒有產生 hook event。改 `CLAUDE_CONFIG_DIR` 也會隔離認證，故依任務要求停止該方向，未複製或搬移憑證。以上失敗嘗試不計入矩陣實測。

## 根因

### 已確認事實

1. 2026-07-19 19:20，phase 4 指令把兩行相對 import 追加到 `~/.claude/CLAUDE.md`。
2. 緊接的 headless session `f96bc555…` 發出兩筆 user memory `include`，parent 正是 `~/.claude/CLAUDE.md`，模型亦讀到內容。
3. 後續正式 headless session `59a276c6…` 沒有 include 收據，只能經 `PostToolUse recovery` 補兩張收據；其 transcript 顯示 `UserPromptSubmit` 執行了 `~/.claude/wtf-sync.sh` 並回報 sync 完成。
4. 現在 `~/.claude/CLAUDE.md` 與 `wtf-config/CLAUDE_CODE.md` SHA-256 同為 `594e62cd…`，兩者都沒有 bundle import。
5. `sync_config.py` 的部署契約是以 `wtf-config/CLAUDE_CODE.md` 產生 `~/.claude/CLAUDE.md`；手改部署副本不具持久性。
6. `~/.claude/settings.json` 現已無 `PreToolUse`，目前是觀察模式，不會再由 gate 阻擋工具。

### 根因判定

**根因不是 headless loader 差異，而是部署漂移：import 沒進 SSOT，之後被同步覆寫。** 第一次 user-only headless 測試成功；後續 session 啟動時已沒有可展開的 import，自然不會有 `InstructionsLoaded include`，gate 依設計 fail-closed。

「具體是哪一次 `sync_config.py sync` 首次移除兩行」為**高可信推論，未取得寫檔稽核紀錄**。同步工具通常保留來源 mtime，因此不能用目標檔 mtime還原確切覆寫時點；但目的檔與 SSOT 位元完全相同、同步會部署該檔、手加行已消失，因果方向明確。

### 同時暴露的部署缺陷

gate、bundle SHA、CLAUDE import 是同一版本單元，卻分三步人工改：先手加 import，再改 settings。任何 sync 或部分失敗都會形成「gate 已啟用、import 不存在」的危險中間態。fail-closed 把部署非原子性放大成全 session 鎖死。

## 解法候選比較

| 候選 | loader 交付保證 | 可用性 | 主要代價／風險 | 判斷 |
|---|---|---|---|---|
| A. 把 import 納入 SSOT，部署時原子更新 bundle、`CLAUDE.md`、settings | **強**；保留 `InstructionsLoaded` 第一手收據 | user/headless 皆由已實測行為支援 | 要處理 SHA 輪替與失敗回復；部署器需防止半套狀態 | **建議** |
| B. gate 接受 project 或核准清單內任一 parent | 強；仍以 loader event 簽收 | 僅在事件確實發出時有效 | 不解決 import 消失；「任一位置」過寬會讓不受控 parent 替 bundle 背書。中央 bundle 的專案外絕對 import 先前又曾不載入 | 只作輔助，不作主修 |
| C. SessionStart hook 注入 bundle 全文並自簽收據 | **中／弱**；證明 hook 讀過並輸出，不證明 Claude loader 已交付 | 不依賴 import，headless 較穩 | 自報式收據削弱原設計目的；stdout 仍可能截斷，且簽收與 context 接收非同一可驗證事件 | 可作降級模式，不宜冒充 loader receipt |
| D. 從 hook input 偵測 headless，headless 改觀察模式 | 無強制保證 | 最不易鎖死 | **未驗證** SessionStart input 有穩定 headless 欄位；用環境變數／`entrypoint` 可能版本漂移；真正漏載時也放行 | 僅作緊急降險 |
| E. user 與 project 都放 import | 理論上可保留 loader event | 某一來源仍在時較有韌性 | 重複部署、SHA 漂移、repo 污染；project 外部 import 限制；目前 gate 的 parent 預設只接受 user CLAUDE，project event 會報錯 | 不建議全面鋪設 |
| F. 專用 headless wrapper，建立含 project-local bundle 的暫存專案後執行 `claude -p` | **強**；沿用已實測 project loader event | wrapper 路徑穩定 | 裸 `claude -p` 仍可能繞過；每次複製 bundle有成本；需治理所有呼叫入口 | 適合高保證批次工作 |

### 候選 B 的安全邊界

若要支援 project parent，不能接受「任一位置」。應同時驗證：

1. `file_path` 必須等於當代 bundle 中 manifest 指定檔，或等於已核准 mirror 且 hash／bytes 完全符合 manifest；
2. `parent_file_path` 必須在部署器產生的核准清單；
3. receipt 綁定 generation、bundle SHA、source SHA；
4. 重複事件可冪等，但任一非核准 parent 事件不得使既有有效收據失效。

這只擴大合法 loader 證據來源，不能取代持久化 import。

## 建議

### 主修：保留 loader receipt，修正部署原子性

1. 先維持現行觀察模式，未完成驗證前不要恢復 `PreToolUse`。
2. 把 bundle import 寫入 SSOT／產生器，不再手改 `~/.claude/CLAUDE.md`。較穩的做法是讓部署器在固定 managed block 產生當代 SHA 兩行，避免人工同步三處。
3. 部署流程改成：建立並驗 hash 完整 bundle → 產生帶同 SHA import 的 CLAUDE 候選檔 → 產生帶同 SHA hook env 的 settings 候選檔 → 全部驗證 → 原子替換。任一步失敗就保持舊三件組。
4. 啟用阻擋前跑 canary：user-only、project-only、both；逐格保存 recorder 原始 JSON，確認兩張 receipt 都是 `InstructionsLoaded/include`，再跑工具放行與 import 缺失的 fail-closed。
5. 加部署後機檢：`CLAUDE.md` 中 SHA、settings 的 `WTF_BUNDLE_SHA256`、bundle 目錄名、manifest digest 四者必須一致；不一致時禁止掛回 `PreToolUse`。

### 輔助方案

- 若高保證 headless 任務需要 project 隔離，使用候選 F wrapper；gate 只接受部署器核准的 project parent。
- 若業務優先於保證，可採候選 C，但 receipt 名稱應改成 `hook_injection`，不可記成 `InstructionsLoaded`，並明載保證降級。
- 不建議依未證實的 headless 偵測自動放行；目前觀察模式是明確、可稽核的全域降險，比隱性分支安全。

## 未完成與禁止宣稱

- 本次因本機 Claude CLI 未登入，沒有補跑 user+project 同時 import；該矩陣格仍是未實測。
- 未執行獨立 Verifier／agy 對抗複驗。
- 未修改 gate、同步器、SSOT 或正式 user settings。
- 不宣稱契約驗收通過。
