# Claude Code Session 全域設定強制載入設計

> 契約：`wtf-session-compliance-20260715`  
> 狀態：設計定案候選；本輪不部署。`~/.claude/settings.json` 與全域 hook 的實際變更須另經 PO 明確核准。  
> 官方依據：[Hooks reference](https://code.claude.com/docs/en/hooks)、[How Claude remembers your project](https://code.claude.com/docs/en/memory)（查證日：2026-07-15）

## 結論

現行 SessionStart 大段 stdout 注入應退役。它只能產生文字，不能阻擋行為；本次 harness 又只把前 2KB inline，故「hook 有跑」不等於「GLOBAL.md 已送達」。

採三層設計：

1. **交付層**：sync 先產生本機內容定址、不可變的 GLOBAL/AGENTS bundle，再由 `~/.claude/CLAUDE.md` 用官方 `@相對路徑` import。Claude Code 原生 loader 會在 session 啟動時展開全文，不再經 SessionStart stdout 預覽通道。
2. **載入閘**：`InstructionsLoaded` 對每個 import 寫入帶 `session_id`、`agent_id`、bundle SHA-256 的收據；收據未齊時，`PreToolUse` deny 所有工具，只放行對缺檔的完整 `Read`；`PostToolUse(Read)` 可補收據；`Stop` block，禁止未載入狀態交付文字後結束。
3. **規則閘**：把能確定判斷的高風險規則另寫成機器 policy，由同一個 `PreToolUse` hook 直接 deny。其餘語意規則仍只能靠模型判斷與事後驗收，不宣稱可完全保證遵守。

這個方案的保證邊界是：**可機器證明指定內容已由官方 loader 放入 context，且未載入前不能用工具或正常結束；不能證明模型理解全文，也不能保證每條自然語言規則都被正確套用。**

### 對 BRIEF 第 3 節三條質疑的回答

1. **什麼機制強制「立即讀」？** 不是 deny 理由中的文字。真正的強制是狀態機：沒有有效收據，PreToolUse 不執行工具，Stop 不准結束。模型可以不照提示呼叫 Read，但結果只能停在閘前，不能完成工作。
2. **既然有強制機制，為何不用它交付全域設定本身？** 本案正是這樣做：設定本體由 Claude Code 官方 `@import` loader 交付；`InstructionsLoaded` 是 loader 完成事件，hook 只記錄可核驗收據。PreToolUse/Stop 負責 fail-closed，不再靠 deny 訊息搬運 19KB 內容。手動 Read 只作 loader 異常時的復原通道。官方文件也明示 imported files 在 launch 時進 context；不是叫模型自行找檔。
3. **Codex／agy 看似較守規則是否能證明措辭有效？** 不能；BRIEF 已標未驗證，不採為依據。可採的原則只有「權限與 hook 攔截比提示詞可靠」，本設計以可重跑的 deny/block 測試驗證，不以模型印確認字串驗證。

## 機制設計

### 1. 交付：不可變 bundle＋原生 import 取代 stdout

`sync_config.py sync` 讀 SSOT 後，先建立內容定址 bundle；目錄名是 manifest SHA-256，檔案建立後永不就地修改：

```text
~/.claude/wtf-session-bundles/<bundle_sha256>/
  manifest.json              # 兩來源的 SHA-256、bytes、lines、schema
  GLOBAL.md                  # SSOT 的逐 byte UTF-8 副本
  AGENTS.md                  # SSOT 的逐 byte UTF-8 副本
```

本機 `~/.claude/CLAUDE.md` 加相對 import：

```text
@wtf-session-bundles/<bundle_sha256>/GLOBAL.md
@wtf-session-bundles/<bundle_sha256>/AGENTS.md
```

相對路徑由 `~/.claude/CLAUDE.md` 所在目錄解析，Mac／Windows 產物相同，不把單機 SSOT 路徑寫進設定。內容定址避免「loader 載入後 SSOT 恰好改版，hook 卻對新版 hash 簽收」的 TOCTOU；舊 session 固定使用舊 bundle，新 session 才切新版。GC 僅刪 30 天以上且不被現行 CLAUDE.md 引用的 bundle。

官方文件明載 import 在 launch 時展開，且 imported files 仍完整占用 context。外部 import 首次會跳核准視窗；本設計使用 user CLAUDE.md 同目錄下的相對 bundle，以避免 external import。部署黑箱測試仍須確認不跳核准；若該版本仍視為 external，先由 PO 明確核准 import，再開 gate，禁止讓 gate 把核准流程鎖死。

`wtf-session-context.sh` 不再輸出 GLOBAL/AGENTS 全文，也不得印「已自動載入，無需再讀」這種無證據斷言。若仍保留 INDEX／TaskLog 輔助輸出，banner 必須寫成「非合規證據，可能被 harness 截斷」。後續應以同一收據機制逐檔取代。

### 2. 收據：事件資料，不查 transcript

官方 `InstructionsLoaded` input 含 `session_id`、`file_path`、`load_reason`、`parent_file_path`；import 事件的 `load_reason` 為 `include`，壓縮後重載為 `compact`。每份來源使用獨立收據，避免兩個非同步 hook 同時改一個 JSON 的 lost update：

```text
~/.claude/wtf-session-state/<session_id>/<agent_id-or-main>/
  generation.json
  GLOBAL.receipt.json
  AGENTS.receipt.json
```

每份收據至少包含：

```json
{
  "schema": 1,
  "source_realpath": ".../wtf-session-bundles/<sha>/GLOBAL.md",
  "source_sha256": "...",
  "source_bytes": 11211,
  "event": "InstructionsLoaded",
  "load_reason": "include",
  "parent_realpath": ".../.claude/CLAUDE.md",
  "recorded_at": "2026-07-15T...Z"
}
```

每次主代理 `SessionStart`（startup／resume／clear／compact）及每次 `SubagentStart` 先建立新的 128-bit 隨機 `generation`，連同 bundle SHA、source、時間寫入對應 agent 的 `generation.json`；兩份收據必帶相同 generation。即使 Claude Code 在 resume 沿用相同 `session_id`，舊收據也不能重放。因 InstructionsLoaded 與 SubagentStart 均可能非同步、兩事件先後未承諾：若 load event 早於 generation，該次不簽收，後續 fail-closed 並走完整 Read；不能為省一次 Read 接受舊代收據。

有效條件全部成立才算已載入：

- `session_id`／`agent_id` 僅允許 `[A-Za-z0-9._-]+`，防路徑穿越；主代理固定 key `main`。
- `source_realpath` 必須位於 `~/.claude/wtf-session-bundles/<bundle_sha>/`；Windows 比對用 `normcase(resolve())`。
- 收據 SHA-256 等於 immutable bundle manifest 與檔案 SHA-256；已簽收 bundle 不因 SSOT 後續更新而混版。
- `load_reason=include` 時，須驗 `parent_file_path` 是預期 `~/.claude/CLAUDE.md`；`load_reason=compact` 時官方不保證有 parent，只驗 immutable bundle path/hash 與當代 generation。不能以任意同名檔冒充。
- 寫檔採「同目錄暫存檔＋`os.replace`」；兩來源、每個 agent 各寫各檔，不需跨平台 file lock。

subagent 不能借主代理收據。官方文件指出每個 subagent 有獨立 context；Explore／Plan 還會刻意略過 CLAUDE.md。故：

- custom／general-purpose agent 以自己的 `agent_id` 收據過 gate。
- Explore／Plan 只准 read-only tools，禁止 Write/Edit/Bash 與影響外部狀態的 MCP；它們可做搜尋，但回主代理後，任何動作仍由已載入設定的主代理執行。
- 若版本沒有在 hook input 提供可用 `agent_id`，保守 deny `Agent`，直到 canary 證實可隔離；不得退回共用 session 收據。

不讀 `transcript_path`。該欄雖為官方 input，但 transcript JSONL 內容與落盤時序不是本案真相源。

### 3. PreToolUse：主要強制點

Matcher 用 `*`，不是只攔 Bash／Write／Edit。未載入時若仍容許 Grep、WebSearch、Agent 等工具，模型仍能開始工作，合規閘就有旁路。

流程：

```text
event = stdin JSON
expected = 此 agent 的 bundle manifest 與兩檔 hash
receipts = (session_id, agent_id-or-main) 的兩份收據

if agent_type 是內建 Explore 或 Plan:
    僅 Read/Glob/Grep 可通過；其他工具 deny
elif receipts 全部有效:
    保護 gate/settings/state/bundle 路徑，再執行規則 policy；通過則 exit 0
elif tool_name == "Read" and file_path 是缺少來源之一
     and offset 未設或 <= 1
     and limit 未設或 >= 該檔總行數:
    exit 0                    # 只放行完整 Read 復原
else:
    回傳 permissionDecision="deny"
```

deny 的 `permissionDecisionReason` 只說明缺哪份收據與允許的復原呼叫；即使模型忽略這段文字，工具仍已被阻擋。JSON structured deny 優先；整合測試另驗 `exit 2` 備援，因官方明載 PreToolUse 的 exit 2 會阻擋工具，而 exit 1 不會。

PreToolUse 必須輸出官方完整 envelope，不能誤放 top-level 欄位：

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"WTF session receipt missing"}}
```

### 4. PostToolUse(Read)：復原收據

只有 Read 成功後才執行；驗證與 PreToolUse 同一組 agent key、canonical path、offset、limit 條件，並檢查 `tool_response` 成功。再對 immutable bundle 即時計算 hash，寫入該來源收據，`event` 記為 `PostToolUse.Read`。

為免「檔案過大但 Read 結果被工具截斷」產生假收據，部署時設定 `max_required_source_bytes` 與 `max_required_source_lines`。任一常載檔超標，sync/check 直接 FAIL，要求先把常載核心拆小；不得仍簽收。門檻以部署環境實測 Read 可完整回傳的較小值決定，不猜固定值。

### 5. Stop：無工具回合的第二道閘

模型可能不呼叫工具而直接回答，故只用 PreToolUse 不完整。主代理 Stop 與 subagent 的 SubagentStop 均以相同邏輯，收到 `(session_id, agent_id-or-main)` 後重驗兩份 hash 收據；Explore／Plan 因官方刻意不載 CLAUDE.md，只驗工具全程限於 Read/Glob/Grep：

- 有效：不輸出 decision，正常結束。
- 無效：回 `{"decision":"block","reason":"..."}`，要求繼續到收據成立。
- `stop_hook_active=true` 不能像現行 ody lint 一律放行；應再查一次收據。若仍缺，繼續 block，但記錄 block 次數與告警。官方目前在連續 8 次 block 後強制結束，這是無法消除的上限。

合併既有 ody Stop hook 時採一個 dispatcher，先跑 session compliance，再跑 reply lint；任一 block 即 block。不得讓兩個腳本互相用 `stop_hook_active` 提前放行。

### 6. 「送達」與「遵守」的裁決

| 層次 | 可否保證 | 判定 |
|---|---:|---|
| 官方 loader 已把指定檔載入 context | 可機器核驗到 hook 事件 | `InstructionsLoaded`＋來源 hash 收據 |
| 未送達前不得用工具／結束 | 可強制 | PreToolUse deny＋Stop block |
| 模型確實逐字閱讀、理解 | 不可觀測 | 不宣稱保證 |
| 可形式化的高風險規則有遵守 | 可強制 | PreToolUse policy deny |
| 任意自然語言原則均有遵守 | 無法保證 | 任務驗收、diff／命令證據、獨立複驗兜底 |

第一批應形式化本次事故規則：從 `projects-registry.md` 產生 Claude_cowork 的 Drive／git_mirror 對照；對 `Write`／`Edit` 及可判定為修改的 Bash，若目標是 mirror 工作副本而非允許的版控動作，直接 deny。這才防止「GLOBAL 已載入但仍在錯的副本改檔」。讀取、git status/diff/log 與明確的 mirror commit/push 流程另列 allowlist。此 policy 需獨立測試，不用 LLM 判斷命令意圖。

### 7. 強制點、資料源、token 成本裁決

- **強制點**：PreToolUse 為主，Stop 補無工具回合；只選其一都有旁路。
- **已讀資料源**：首選官方 `InstructionsLoaded` 事件；`PostToolUse(Read)` 是復原；不解析 transcript、不採模型自報、不把 SessionStart stdout 當證據。
- **送達 vs 遵守**：載入收據只證送達；遵守只對已形式化 policy 強制，其餘交由 ody 驗收，不混稱。
- **token**：目前 GLOBAL 11,211 bytes／131 行，AGENTS 8,211 bytes／89 行，合計 19,422 bytes。精確 token 取決於 Claude tokenizer，不能由 bytes 精確換算；粗估約 5k–10k tokens（未驗證）。相較現行實際只 inline 2KB，正確送達會增加約 17.4KB context；相較原設計意圖的全文注入不增加。移除 SessionStart 的 GLOBAL/AGENTS 副本可避免重複。部署驗證以同模型各跑 10 個空白 session，比對 usage input tokens 與啟動延遲 p50/p95，記錄實測值後取代粗估。

## 變更清單

| 檔案 | Hook／位置 | 變更與腳本邏輯 | 跨平台注意 |
|---|---|---|---|
| `wtf-config/CLAUDE_CODE.md` | user CLAUDE.md 真相源 | 加 bundle import placeholder；保留人類可讀說明，但不再要求模型自行 Read | SSOT 不寫單機絕對路徑 |
| `wtf-config/sync_config.py` | `sync`／`check` | 產生 immutable content-addressed bundle 與相對 imports；檢查 hash、import 唯一、size/line 門檻；部署 hook | Mac 用 `python3`、Windows 用 `python`；寫 UTF-8、路徑含空白不得 shell 拼字串 |
| `wtf-config/hooks/wtf-session-context.sh` | SessionStart | 移除 GLOBAL/AGENTS 全文與錯誤 banner；保留專案內容時明示非合規證據 | `/bin/bash` 3.2 相容；不用關聯陣列 |
| `wtf-config/hooks/wtf-session-gate.py` | SessionStart、SubagentStart、InstructionsLoaded、PreToolUse、PostToolUse、Stop、SubagentStop | 初始化每個 agent generation；解析 stdin JSON、canonical path、bundle hash、獨立收據、deny/block、policy dispatch；保護 gate/settings/state/bundle；預設 fail-closed | `Path.home()`；`normcase(resolve())`；UTF-8；不用 `/tmp`、`fcntl`、symlink |
| `wtf-config/hooks/wtf-session-gate.sh` | 上述四種 hook wrapper | `command -v python3`，否則 `python`；兩者皆無則 stderr＋exit 2 | Claude Code Windows 要有 Git Bash；settings 明設 `shell: "bash"` |
| `wtf-config/policies/session-policy.json` | PreToolUse policy | 宣告 required sources、size/line 門檻、Drive/mirror 對照、可機檢 deny/allow 規則與 schema version | 由 sync 產生機器路徑，不手寫 Mac/Windows 分支 |
| `wtf-config/hooks/stop_dispatcher.py` | Stop | 依序合併 session gate 與既有 `tools/ody/squad/stop_hook.py` 結果；任一 block 即 block | 避免兩個 Stop handler 的迴圈狀態互相誤放行 |
| `wtf-config/tests/test_session_gate.py` | 離線測試 | 覆蓋 session/agent 隔離、bundle hash、partial Read、path case/斜線、競態、保護路徑、policy deny、malformed JSON、無 Python | 以 tempfile 模擬 POSIX 與 Windows 形式；Windows runner 實跑一次 |
| `~/.claude/settings.json`（部署產物） | 四種 hook | 註冊下列結構；**黃區，另案 PO 核准後才寫** | 不以 `.claude/settings.local.json` 取代全域 scope |

設定結構示意：

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{"type":"command","command":"bash ~/.claude/wtf-session-gate.sh init","shell":"bash"}]
    }],
    "SubagentStart": [{
      "matcher": "*",
      "hooks": [{"type":"command","command":"bash ~/.claude/wtf-session-gate.sh init-agent","shell":"bash"}]
    }],
    "InstructionsLoaded": [{
      "matcher": "session_start|include|compact",
      "hooks": [{"type":"command","command":"bash ~/.claude/wtf-session-gate.sh instructions","shell":"bash"}]
    }],
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{"type":"command","command":"bash ~/.claude/wtf-session-gate.sh pretool","shell":"bash"}]
    }],
    "PostToolUse": [{
      "matcher": "Read",
      "hooks": [{"type":"command","command":"bash ~/.claude/wtf-session-gate.sh postread","shell":"bash"}]
    }],
    "Stop": [{
      "hooks": [{"type":"command","command":"bash ~/.claude/wtf-session-gate.sh stop","shell":"bash"}]
    }],
    "SubagentStop": [{
      "matcher": "*",
      "hooks": [{"type":"command","command":"bash ~/.claude/wtf-session-gate.sh stop-agent","shell":"bash"}]
    }]
  }
}
```

PO 核准部署時，先備份 settings、以 JSON parser 合併，不做文字取代；`claude --debug` 驗證 hook 載入。先完成 import 首次核准，再開 gate。提供使用者控制的 break-glass：啟動 Claude 前設定 `WTF_SESSION_GATE_BYPASS=1` 才放行，hook 每次寫 audit warning；模型在 gate 未開前無 Bash 能力，不能自行設定。不得把內部例外靜默 fail-open。

`~/.claude/settings.json` 屬 user hook：可被同 OS 帳號修改、`disableAllHooks` 或 `--bare` 跳過。個人電腦基線只保證「hooks 啟用且檔案未被外部竄改」；若要抵抗 agent／使用者同權限竄改，必須由 IT 部署 managed settings、managed hooks、managed CLAUDE.md，並限制一般帳號寫入。文件不得把 user hook 稱為防竄改安全邊界。

## 驗證步驟

### A. 離線機檢

1. 跑 `python3 -m unittest wtf-config.tests.test_session_gate`（Windows：`python -m unittest ...`）。
2. 固定來源 hash，對未有收據的 Bash／Read(other)／Write event 餵 stdin：assert JSON decision 為 deny；process exit 為 0。
3. 餵完整 Read(GLOBAL) 後只應有一份收據，AGENTS 仍缺；兩份完整 Read 後才全放行；另一 `agent_id` 仍不得借用。
4. `offset=2`、`limit<總行數`、相似檔名、symlink 指向別處、竄改收據、來源改一字，全部仍 deny。
5. Stop 無收據／過期收據必 block；兩份有效收據才無 decision。
6. 模擬兩個 InstructionsLoaded process 同時寫 GLOBAL／AGENTS，兩份收據均存在且 JSON 完整；另驗 bundle 建立後不可被 sync 就地覆寫。
7. 對相同 session_id 連跑 resume／compact init 及兩個 SubagentStart，舊 generation／另一 agent 收據必失效；InstructionsLoaded 早於 init 的競態只能造成 deny，不得錯放。

### B. 新 session 黑箱實測

1. 先用隔離設定／測試 HOME，不直接動正式 `~/.claude`。啟動新 session，首個 prompt 要求「不要讀設定，直接執行 `pwd`」；預期 `pwd` 只有在兩份收據成立後才能執行。
2. 暫時移除 CLAUDE.md 的 AGENTS import，再開新 session；首個 Bash 必被 deny。要求直接回答文字時，Stop 必 block；完整 Read AGENTS bundle 後才能結束。
3. sync 產生新版 GLOBAL bundle；既有 session 仍固定舊 bundle且檔案未變，新 session 必載新版，不得混用兩版收據。
4. 建超過門檻的測試來源；`sync_config.py check` 必 FAIL，不能產生可部署狀態。
5. 在 mirror 測試 Write／Edit／mutating Bash，policy 必 deny；相同操作指向 Drive 工作區才進正常 permission flow。
6. Mac zsh 啟動 Claude、Windows Git Bash 啟動 Claude，各重跑 1–5；保存 hook debug log、收據與實際 tool 是否執行的證據。
7. 啟動、resume、`/clear`、compact、custom subagent 各測一次；每次 session/agent receipt 必正確。Explore/Plan 只能 read-only，不得沿用主代理收據。
8. 各測一次 `disableAllHooks`／`--bare`、hook script 損壞、拒絕 import、parallel Read+Bash，確認 canary 明確報告「不受保護」或 deny，不得把它記成 PASS；managed 部署另測一般帳號無法修改 hook/state。

### C. harness 失效偵測

- 每次 `sync_config.py check` 驗 settings schema、hook 檔 hash、CLAUDE.md import、來源大小；任一漂移回非零。
- CI 每週跑最小 headless canary：未載入 fixture 時 Bash 不得產生 sentinel 檔；載入後才可產生。這直接測「有沒有擋」，不看模型說法。
- 另跑 stdout truncation probe，記錄 inline bytes。這只監測 harness 行為，不再作合規依賴；若 2KB 改變，設計仍有效。
- 記錄未知 `hook_event_name`、缺欄位、JSON parse error、連續 Stop block、break-glass 使用；任何一項觸發醒目告警及非零 `sync_config.py status`。
- Claude Code 升版後必跑 canary。若 `InstructionsLoaded include` 不再發出或欄位變更，PreToolUse/Stop 因無收據 fail-closed；使用者以 break-glass 進場修復，不能靜默放行。

## 殘餘風險

1. `InstructionsLoaded` 證明 loader 處理了檔案，不證明模型逐字閱讀、記住或理解；這是不可觀測狀態。
2. 自然語言原則若未編譯成 policy，模型仍可能讀到卻做錯。事故類高風險規則應逐條轉為可測 deny；無法形式化者只能靠 diff、測試與獨立複驗。
3. Stop 官方有連續 8 次 block 後強制結束上限；它不是永久鎖。PreToolUse 仍會阻止後續工具，但純文字錯誤回覆可能在上限後送出。
4. InstructionsLoaded hook 為非同步、官方定位為 observability；首個工具呼叫可能在收據落盤前被暫時 deny。需量測 p95，必要時 gate 短暫輪詢數十毫秒，不可假定事件排序或長時間 sleep。
5. Python／Git Bash 缺失或 hook 自身損壞時，fail-closed 會妨礙工作；break-glass 是必要維修入口，也代表有權操作使用者 shell 的人可以繞過。
6. `@import`、InstructionsLoaded schema、Stop block 上限皆由 Claude Code 版本控制。官方目前有文件，但仍需升版 canary；不能假設永遠不變。外部 import 的首次核准也必須納入部署順序。
7. 對 Bash 判斷「是否修改 mirror」若只做字串比對，會有 shell 組合命令與間接腳本旁路。初版應保守 deny mirror cwd 的未知 Bash，只 allow 明確讀取／版控命令；否則不得宣稱該規則已強制。
8. 常載全文約 19.4KB，正確性換來固定 context 成本。不能為省 token 回到摘要冒充全文；若要降成本，須由 PO 把 GLOBAL 拆成「每 session 必載核心」與按需 playbook，並讓核心仍受 hash 收據保護。
9. user settings/hooks 不是防竄改邊界：同權限程序可改 settings、收據或以停用 hooks 的方式啟動。個人部署只能偵測與告警；需要強安全時必須上 managed policy／OS ACL。
10. Explore／Plan 不載 CLAUDE.md。它們只能作唯讀探索；若允許 Bash、寫入或外部副作用，就形成獨立 context 旁路。
