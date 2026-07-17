# Claude Code Session 全域設定強制載入最終提案

> 契約：`wtf-session-compliance-20260715`  
> 文件定位：取代 `DESIGN.md`，作為交 PO 裁決的唯一文件。  
> 範圍：本輪只提案，不部署；不得修改正式 `~/.claude/settings.json` 或全域 hooks。  
> 事實基準：`BRIEF.md`、`VERIFY_ROUND1.md`、`VERIFY_ROUND2.md`；未知事項一律留待隔離 canary。

## 結論

1. 退役以 SessionStart 大段 stdout 交付 GLOBAL／AGENTS 的作法；本案實證顯示它只 inline 前 2KB，不能作送達證據。
2. 改由內容定址的不可變 bundle，加上 user `CLAUDE.md` 的原生 `@import` 交付全文。
3. 以 `InstructionsLoaded`、來源 hash、session／agent generation 建立收據；未有有效收據時，`PreToolUse` 阻擋工具。
4. `Stop`／`SubagentStop` 只作純文字回合的第二道閘；連續 block 的最終安全閥行為未知，不宣稱永久阻擋。
5. loader 異常時只允許一次完整 `Read` 復原；compact 正常以 `load_reason=compact` 事件重簽，避免反覆讀全文。
6. 此設計可證明指定檔案經 loader 處理，並強制可形式化規則；不能證明模型理解或遵守全部自然語言。
7. 先完成離線測試與隔離 HOME canary；全部 PASS 且 PO 再核准，才可碰正式 `settings.json`。

## 已證實前提

| 前提 | 證據／裁決 | 設計影響 |
|---|---|---|
| 現行 SessionStart stdout 本案產出 30,968 bytes，但 harness 只 inline 前 2KB；關鍵規則在 byte offset 3613 | `BRIEF.md`、`VERIFY_ROUND1.md` | stdout 不得再作合規送達通道或收據 |
| `InstructionsLoaded` 事件存在；文件載明 `session_id`、`file_path`、`load_reason`，並有 `include`、`compact` 等 reason | `VERIFY_ROUND2.md` 第一手裁決 | 可作 loader 事件資料源，但須對 schema 漂移 fail-closed |
| `parent_file_path` 未見於第一手文件 | `VERIFY_ROUND2.md` R1 | 只能 feature-detect：有欄才驗，缺欄不得單獨阻擋 |
| user `CLAUDE.md` 支援 `@import`，launch 時展開；外部 import 首次需核准 | `VERIFY_ROUND2.md` | 使用同目錄相對 bundle；仍須先驗核准流程，再啟用 gate |
| `PreToolUse` 可回 `permissionDecision=deny`；exit 2 是 blocking error，exit 1 不阻擋 | `VERIFY_ROUND2.md` | 主要強制點採 structured deny，exit 2 只作失敗備援 |
| `Stop` 可回 block，但官方資料未證實「連續 8 次後強制結束」 | `VERIFY_ROUND2.md` R2 | 保留 Stop 為第二道閘，不寫死次數或永久保證 |
| `SubagentStart` 事件存在 | `VERIFY_ROUND2.md` | 可設計 agent 隔離；實際 agent key 欄位仍待 canary |
| `disableAllHooks` 可停用 hooks；`--bare` 的官方定義是 minimal mode、略過自動探索，不等於略過 hooks | `VERIFY_ROUND2.md` R3 | 防竄改邊界只列前者與同權限編輯；`--bare` 不列旁路 |
| 本契約 events 目前只有 `contract_created`，沒有 `check` | `tools/ody/data/events.jsonl`、`VERIFY_ROUND2.md` R5 | 本文件不得宣稱已驗收、已完成或已通過獨立複驗 |

## 未證實、待 canary 項

| 待驗項目 | PASS 判準 | FAIL 處置 |
|---|---|---|
| `parent_file_path` 在目前 Mac／Windows 版本是否出現、各 load reason 的形態 | 有欄時 canonical path 指向預期 user `CLAUDE.md`；缺欄時其他條件仍可完成收據 | 保持 feature-detect；不得把缺欄升格為錯誤 |
| `InstructionsLoaded` 與 SessionStart／SubagentStart 的事件順序、並行與落盤延遲 | 收據不錯綁 generation；p95 延遲可接受；競態只暫時 deny、不錯放 | 調整原子初始化／短輪詢；仍不穩則不部署 |
| hook input 是否提供可穩定區分 subagent 的 key | 不同 agent 無法借用主代理或彼此收據 | 若無穩定 key，先停用有副作用的 Agent／subagent，不共用收據 |
| 同目錄相對 `@import` 是否免外部 import 核准 | 隔離 HOME 首次啟動不出現未處理核准，或可在開 gate 前由 PO 明確完成核准 | 不得先開 gate；改部署順序或退回提案修訂 |
| compact 後是否可靠發出可重簽的 `load_reason=compact` 事件 | 不需 Read 即重建兩份有效收據，且不沿用舊 generation | 只允許該 generation 每來源一次 Read 復原；再失敗即告警並停止自動復原 |
| Stop／SubagentStop 連續 block 的實際安全閥 | 量出目前版本的終止、重試及 `stop_hook_active` 行為並保存 log | 下修純文字回合保證；不得用未證實次數設計安全性 |
| `--bare` 下 hooks 的實際行為 | 報告觀察值，不以任何結果改寫其官方 minimal mode 定義 | 若 hooks 未啟用，列為 canary 發現的版本行為，不宣稱官方旁路 |
| Explore／Plan 的載入內容、hook 欄位與工具邊界 | 證明無主代理收據借用，且只允許 Read／Glob／Grep | 無法隔離即先禁用，或禁止所有有副作用工具 |
| 完整 Read 的安全 bytes／lines 上限 | 在兩平台證明工具回傳未截斷，取較小實測值 | 超標時 `sync/check` FAIL，要求縮小常載核心 |
| 新方案 token 與啟動延遲 | 同模型各 10 個空白 session，取得 input tokens、p50／p95 | 交 PO 重估成本；不得以 bytes 假稱精確 token |

## 機制設計

### 1. 交付層：不可變 bundle＋原生 import

`sync_config.py sync` 從 SSOT 逐 byte 複製 GLOBAL／AGENTS，建立以 manifest SHA-256 命名的 bundle：

```text
~/.claude/wtf-session-bundles/<bundle_sha256>/
  manifest.json
  GLOBAL.md
  AGENTS.md
```

`manifest.json` 記錄 schema、兩檔 SHA-256、bytes、lines。bundle 建立後不得就地覆寫；舊 session 固定舊 bundle，新 session 才切新版。user `~/.claude/CLAUDE.md` 使用同目錄相對 import：

```text
@wtf-session-bundles/<bundle_sha256>/GLOBAL.md
@wtf-session-bundles/<bundle_sha256>/AGENTS.md
```

GC 只刪超過保留期、未被現行 `CLAUDE.md` 引用且沒有活躍 session state 指向的 bundle。現行 `wtf-session-context.sh` 移除 GLOBAL／AGENTS 全文及「已自動載入」斷言；若保留 INDEX／TaskLog 輸出，須標示「非合規證據，可能被截斷」。

### 2. 收據層：每 session、每 agent、每來源獨立

狀態路徑：

```text
~/.claude/wtf-session-state/<session_id>/<agent_key>/
  generation.json
  GLOBAL.receipt.json
  AGENTS.receipt.json
  recovery.json
```

SessionStart／SubagentStart 建立 128-bit 隨機 generation；`session_id`、`agent_key` 只接受 `[A-Za-z0-9._-]+`。收據至少記錄 generation、bundle SHA、canonical source path、source SHA-256、bytes、事件、load reason 與時間。每來源獨立以同目錄暫存檔加 `os.replace` 寫入，避免 lost update，不依賴 `/tmp`、`fcntl` 或 symlink。

有效收據須同時符合：

- generation 等於目前 session／agent generation；不得借用舊 session、主代理或另一 agent 的收據。
- source canonical path 位於目前 bundle；Windows 使用 `normcase(resolve())`。
- 實檔 SHA-256 等於 manifest 與收據；任一不符即失效。
- `load_reason=include` 時：若 input 含 `parent_file_path`，canonical 後必須是預期 user `CLAUDE.md`；若欄位不存在，記 `parent_check="unavailable"`，只依其餘已文件化條件判定，不因缺欄阻擋。
- `load_reason=compact` 時同樣 feature-detect `parent_file_path`；核心判定仍是當代 generation、bundle path 與 hash。
- 未知 load reason、未知 schema、JSON parse error 一律不簽收並告警。

`parent_file_path` 是未文件化欄位，不得成為必要 schema，也不得因觀察到一次就寫成永久假設。

### 3. PreToolUse：主要強制點

Matcher 使用 `*`。流程如下：

```text
讀取 event、目前 generation、manifest 與兩份收據

若 agent 屬已驗證的 Explore／Plan：
    僅允許 Read／Glob／Grep，其餘 deny
否則若兩份收據皆有效：
    先保護 gate／settings／state／bundle 路徑
    再執行 session policy；通過才 exit 0
否則若 Read 正好指向缺少來源、從首行開始且要求完整行數，
         且該 generation／來源尚未用過復原額度：
    放行一次 Read 復原
否則：
    structured deny
```

deny 使用官方 envelope：

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"WTF session receipt missing"}}
```

deny reason 只作說明，不是強制來源。無法輸出合法 JSON 時以 exit 2 阻擋；不得使用 exit 1 假裝 fail-closed。

### 4. compact 與一次性 Read 復原

正常 compact 路徑不要求再次讀全文：generation 更新後，對兩個 immutable bundle 檔發出的 `InstructionsLoaded(load_reason=compact)` 事件可直接重簽收據。這是預設路徑，也是避免 token 反覆膨脹的主要措施。

只有 loader 事件缺失、競態或欄位異常時，才開啟 Read 復原；限制如下：

1. 每 generation、每來源最多放行一次完整 Read；額度以 `recovery.json` 原子記錄。
2. `PostToolUse(Read)` 只在 tool response 成功、path／offset／limit／hash 全部符合時補收據。
3. 復原後若再次 compact，應由新的 compact 事件重簽，不自動再次 Read。
4. 同一 session 連續兩個 generation 需要 Read 復原，或任一 generation 復原後仍缺收據，立即告警、保持 deny，要求使用者以 break-glass 維修；不得形成「Read→context 膨脹→compact→再 Read」死循環。
5. `sync/check` 對 required source 設實測 bytes／lines 上限；超標直接 FAIL，不簽假收據。

### 5. Stop／SubagentStop：第二道閘

Stop 重新驗兩份收據：有效則不輸出 decision；無效則回 `{"decision":"block","reason":"..."}`。`stop_hook_active=true` 時仍重驗收據並記錄 block 次數，不能無條件放行。既有 ody reply lint 與 session gate 由單一 dispatcher 合併，任一 block 即回 block。

Stop 的連續 block 安全閥與最終終止行為目前未知。故保證只能寫成：PreToolUse 可阻擋後續工具；Stop 在已觀察到的 block 能力內攔截純文字收尾，但是否可無限阻擋須由 canary 裁決。不得再引用「8 次」或其他固定數字。

### 6. 規則 policy 與保證邊界

第一批 policy 從 `projects-registry.md` 產生 Drive／git_mirror 對照。對 Write／Edit 與可判定為修改的 Bash，若目標是 mirror 工作副本而非明列版控動作，直接 deny；讀取與明確的 `git status`／`diff`／`log`／核准後 commit／push 分列 allowlist。未知 Bash 在 mirror cwd 預設 deny，避免只靠字串比對宣稱安全。

| 層次 | 能否保證 | 判定方式 |
|---|---:|---|
| loader 處理指定 bundle | 可機器核驗 | `InstructionsLoaded`＋path／hash／generation 收據 |
| 未送達前使用工具 | 可阻擋 | PreToolUse deny |
| 未送達時純文字結束 | 有限度阻擋 | Stop block；最終安全閥待 canary |
| 模型逐字閱讀、理解 | 不可觀測 | 不作保證 |
| 可形式化高風險規則 | 可強制 | PreToolUse policy deny |
| 其餘自然語言原則 | 無法完全保證 | diff、測試與後續正式驗收 |

### 7. 防竄改與維修邊界

user settings／hooks 不是安全邊界。同 OS 權限的程序可直接改檔，使用者也可設定 `disableAllHooks`；兩者是本提案承認的旁路。`--bare` 只代表 minimal mode、略過自動探索，不列為跳過 hooks 的已知旁路。

break-glass 由使用者在啟動 Claude 前設定 `WTF_SESSION_GATE_BYPASS=1`，每次使用寫 audit warning；不得由 gate 內部錯誤靜默 fail-open。若需要抵抗同權限竄改，另案採 managed settings／managed hooks／OS ACL，不得把個人部署包裝成此級保護。

## 分階段部署計畫

### 階段 0：提案裁決

- 本文件僅供 PO 決定是否進入實作。
- 不修改 `wtf-config/`、`~/.claude/CLAUDE.md`、hooks 或 settings。
- **PO 核准點 0**：核准機制、保證邊界、token 成本量測方式，以及「先隔離、後正式」原則；未核准即停止。

### 階段 1：離線實作與單元測試

- 只在 repo 內新增 bundle 產生器、gate、policy、dispatcher 與 tests。
- 測 session／agent 隔離、hash、partial Read、feature-detect、競態、原子寫入、一次性復原、連續復原告警、Stop block、保護路徑、malformed JSON、Python 缺失。
- 不安裝 hooks，不改任何 HOME settings。
- **PO 核准點 1**：檢視 diff、測試輸出、未碰正式 HOME 的證據；全部 PASS 才准進隔離 canary。

### 階段 2：隔離 HOME canary

- 使用暫存 HOME 與獨立 settings／state／bundle；不得讀寫正式 `~/.claude`。
- 依「未證實、待 canary 項」逐項測 startup、resume、`/clear`、compact、custom subagent、Explore／Plan、並行事件、拒絕 import、hook 損壞、`disableAllHooks` 與 `--bare`。
- 用 sentinel 證明缺收據時 Bash／Write 未執行；保存 debug log、hook stdin、收據、exit code 與 token／延遲數據。
- Mac 與 Windows 各跑；任一平台 FAIL 即退回階段 1，不得降低判準放行。
- **PO 核准點 2**：逐項審 canary 報告；只有零未解 P0／P1、所有部署必要項 PASS，才可規劃正式機 canary。

### 階段 3：正式機、非正式 settings 的影子檢查

- 在正式 HOME 只部署不可執行的 bundle 與 `sync_config.py check` 影子檢查；不註冊 gate hooks、不改正式 `settings.json`。
- 驗 bundle hash、相對 import 產物、來源上限、GC 計畫與 settings JSON merge 結果的 dry-run。
- 先完成 import 核准流程演練，確定不會被 gate 鎖死。
- **PO 核准點 3**：審 dry-run diff、備份／回復命令與 break-glass 演練；明確授權後，才可修改正式 `~/.claude/settings.json`。

### 階段 4：正式 settings 小流量 canary

- 先備份 settings；以 JSON parser 合併，不做文字取代；只在一台機器、限定時窗啟用。
- 首輪只開收據與 PreToolUse gate；確認穩定後再開 Stop dispatcher 與 mirror policy，逐層擴大。
- 每層驗 startup、compact、工具 deny、純文字 Stop、break-glass、回復；任一異常立即還原備份。
- **PO 核准點 4**：審正式 canary 證據；核准後才擴至第二台機器與常態啟用。

### 階段 5：常態監測

- `sync_config.py check` 驗 settings schema、hook hash、imports、bundle hash、來源上限與 state 異常。
- Claude Code 升版後重跑隔離 canary；每週最小 headless canary 以 sentinel 驗 deny，不看模型自報。
- 告警項：未知 event／欄位、parse error、連續 Stop block、連續 Read 復原、break-glass、settings 漂移。
- **PO 核准點 5**：核准監測頻率、log 保留期與升版阻擋政策；未核准不自動擴張權限或範圍。

## 變更清單

| 檔案／位置 | 變更 | 何時可動 |
|---|---|---|
| `wtf-config/CLAUDE_CODE.md` | 加 bundle import placeholder；移除靠模型自行 Read 的合規假設 | 階段 1，PO 核准點 0 後 |
| `wtf-config/sync_config.py` | 產 immutable bundle、imports、hash／size／line check、dry-run settings merge、GC 保護 | 階段 1 |
| `wtf-config/hooks/wtf-session-context.sh` | 移除 GLOBAL／AGENTS 全文與無證據 banner | 階段 1；正式部署到 HOME 依階段 4 |
| `wtf-config/hooks/wtf-session-gate.py` | generation、feature-detect 收據、PreToolUse、PostToolUse、Stop、一次性復原、告警 | 階段 1 |
| `wtf-config/hooks/wtf-session-gate.sh` | Mac／Windows Git Bash wrapper；Python 缺失時 fail-closed | 階段 1 |
| `wtf-config/hooks/stop_dispatcher.py` | 合併 session gate 與 ody reply lint；任一 block 即 block | 階段 1 |
| `wtf-config/policies/session-policy.json` | required sources、實測上限、Drive／mirror 規則、schema | 階段 1 |
| `wtf-config/tests/test_session_gate.py` | 離線測試與競態／死循環回歸案例 | 階段 1 |
| 隔離 HOME 下的 `.claude/*` | canary bundle、state、hooks、settings | 階段 2，PO 核准點 1 後 |
| 正式 `~/.claude/CLAUDE.md` | 切換相對 bundle imports | 階段 4，PO 核准點 3 後 |
| 正式 `~/.claude/settings.json` | 註冊 SessionStart、SubagentStart、InstructionsLoaded、PreToolUse、PostToolUse、Stop、SubagentStop | **階段 4，須 PO 明確授權** |

## 殘餘風險

1. `InstructionsLoaded` 只能證明 loader 處理檔案，不能證明模型閱讀、理解、記住或正確套用。
2. Stop 的連續 block 安全閥未知；在 canary 定性前，不能保證阻止所有純文字違規回覆。PreToolUse 只能阻止工具，不能攔已生成文字。
3. `parent_file_path` 未文件化。feature-detect 降低版本相容風險，也降低了 include 來源父層的鑑別強度；剩餘信任落在 immutable bundle path／hash／generation。
4. InstructionsLoaded 與 lifecycle hooks 可能非同步；fail-closed 會造成暫時 deny。短輪詢只能降低摩擦，不能假定事件順序。
5. compact event 若缺失，Read 復原仍會增加 context。額度與連續復原熔斷可避免無限循環，但代價是 session 可能停住，需使用者維修。
6. 全文約 19.4KB 的固定 context 成本仍在；實際 token 與延遲尚未量測。要降成本只能由 PO 縮小常載核心，不能用摘要冒充全文。
7. user settings／hooks／state 可被同權限程序改寫，`disableAllHooks` 可停用 hooks；個人部署不是防竄改邊界。`--bare` 不列為已知旁路。
8. break-glass 是必要維修入口，也是真實旁路；audit 只能留下證據，不能阻止有權使用者啟用。
9. mirror Bash policy 若解析不完整，組合命令、間接腳本、子程序可能旁路。初版須保守 deny；因此也可能誤擋合法命令。
10. Explore／Plan 或其他 subagent 若缺穩定 agent key，只能禁用有副作用能力；這會降低代理功能，不能以共用收據換便利。
11. Python、Git Bash、hook 腳本或 settings 損壞時，fail-closed 會妨礙工作；回復流程必須先在隔離 HOME 實測。
12. Claude Code 升版可能改 hook schema、event 時序或 import 行為。升版 canary 是必要條件，但仍不能消除零日變更風險。
13. 本文件目前沒有 ody coach check 紀錄；不得據此宣稱提案已驗收或契約已完成。
