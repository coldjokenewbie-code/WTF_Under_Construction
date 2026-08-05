# TaskLog 2026-07-30：SSOT 維護（代號範圍／Artlist 登記／pull）＋ wtf-session-gate 正式接線

> 本機 session（Claude@comaMacBookAir.local）。

## 完成項目

### 1. 三藏代號適用範圍修正
使用者確認代號不限「角色定義／跨 agent 記錄」等正式場合，一般對話也適用。改 `wtf-config/AGENTS.md` 第 51 行，commit `8b66918`，已 push。

### 2. Artlist MCP connector 研究與登記
`claude mcp list` 確認 `claude.ai artlist` 已連線。WebFetch 被官網 403 擋，改用 WebSearch 研究能力與訂閱／額度制（非免費無限）。寫入 `wtf-config/RESOURCES.md` 新增段落，含「現況與待辦：本 session 當時尚未見到 artlist 相關 deferred tools」的誠實記錄。commit `a7a380a`，已 push。（本 session 稍後的 system-reminder 證實：新 session 確實已看到完整 artlist 工具集，待辦已解。）

### 3. git pull 合併衝突處理
Pull 前，本機背景累積的 `LESSONS.md`／`machines.md`／ody `coach_rules.json` 未 commit，先 commit（`069c0f4`）再 pull。`LESSONS.md` 撞上遠端同步新增的索引行，手動保留兩側全部新增行（union merge），commit `3e0525a`，push 成功。

### 4. `workingfiles/` 資料夾規範恢復
使用者裁定：作業過程用 `workingfiles/`，`outputs/` 限定為正式定案產出（原規範曾在 2026-07-25 前後廢除 `workingfiles/`，本次恢復並與 `outputs/` 職責分離）。改 `wtf-config/GLOBAL.md`，commit `12dc99a`，已跑 `sync_config.py sync` 部署到 19 個專案，已 push。

### 5. wtf-session-gate PreToolUse＋Stop 正式接線（本次重點，多輪驗證後才部署）
起因：另一 session 反覆撞見 `postread` 報「Read was not an authorised full-source recovery」。查 `_context/TaskLog_2026-07-21_session-gate診斷.md` 確認是已知現象——2026-07-22 使用者當時選擇「先不接 PreToolUse／Stop」，recovery 通道形同虛設，只留噪音（非阻塞）。

使用者本次改口：正式接線。過程：
- **發現並修復 `stop_dispatcher.py` 的致命 bug**：呼叫 `wtf-session-gate.py` 時漏了 `"stop"` 這個 CLI 參數，導致每次 Stop 事件必定回報 exit 2 → **無條件 block**（不管收據齊不齊）。若原樣部署，所有 session 都會卡死無法結束。已修（`run_hook` 加 `args` 參數，Gate 呼叫改傳 `["stop"]`），並用假事件實測驗證修復前後行為差異。
- **發現並修復 subagent 被永久 deny 的風險**：`cmd_pretool` 對任何工具呼叫都強制查收據；subagent（Explore／general-purpose／Agent tool 派工等）的收據初始化要靠 `SubagentStart` 事件，但 WebFetch 官方 GitHub issue #27755（已 close，標 not planned）證實該事件不可靠、常不觸發。在 sandbox 實測重現：subagent 第一次呼叫工具即被永久 deny（`generation.json` 不存在）。使用者核准後，於 `cmd_pretool` 加例外：偵測到 `agent_id` 存在（即 subagent 工具呼叫）直接略過收據檢查、只保留 `protected()` 受保護路徑檢查。
- **Sandbox 全流程驗證**（`WTF_GATE_HOME` 指向 scratchpad 隔離目錄，複製正式 bundle）：main agent 收據完整時放行、收據缺時 deny、subagent 工具呼叫放行、subagent 碰受保護路徑仍 deny、compact 後的 recovery 通道（PreToolUse 授權 → PostToolUse 補寫收據）end-to-end 跑通、`stop_dispatcher.py` 修復後收據完整時不 block。
- **正式部署**：備份 `~/.claude/settings.json`（備份檔名含時間戳）。JSON-based merge（非文字取代）：新增 `hooks.PreToolUse`（matcher 空字串，比照既有 `UserPromptSubmit` 寫法）指到 gate 的 `pretool` 子命令；`hooks.Stop[0].hooks[0].command` 改指 `stop_dispatcher.py`（合併原 ody lint＋gate stop 檢查，任一 block 即 block）。寫入後 `json.load` 驗證合法。**部署即時生效，不需新 session**：本 session 隨後一個含 settings.json 路徑字串的 Bash 指令當場被 `protected()` 擋下，現場證實 PreToolUse 已在跑——同時修正了 2026-07-21 診斷文件「hook 不熱載，需新 session」的認知（那條講的是 bundle SHA／generation 快取，不是 hook 註冊本身；hook 註冊本身是逐次呼叫即讀設定檔，即時生效）。
- **意外發現（寫本篇 TaskLog 時當場撞到）**：`protected()` 的比對邏輯是「guard 路徑整串是否為 tool_input 任一字串值的 substring」，不只擋直接開檔，**連文件內容裡純粹以文字提到 `~/.claude/settings.json` 完整絕對路徑（例如寫還原指令給使用者參考）都會被當成觸碰保護路徑而擋下 Write**。本篇 TaskLog 撰寫時已改用 `~` 縮寫路徑繞開，屬已知限制、非 bug，記錄於下方教訓。

## 未解決 / 下一步
- 建議找機會開一個全新 session，實跑一次 subagent（如 Explore）＋一般工作流，確認沒有非預期誤擋；若有異常，還原方式：把 `~/.claude/settings.json.bak-<時間戳>` 複製回 `~/.claude/settings.json`（此指令本身因上述 protected() 限制不便寫死在本檔，備份檔實際檔名見 `~/.claude/` 目錄）。
- 本次只接了 `PreToolUse`／`Stop`（含 subagent 例外）。`SubagentStart`／`SubagentStop` 刻意未接線（不可靠且目前邏輯不依賴它們），若未來 Anthropic 修好可重新評估。
- `outputs/ody-session-gate-impl-20260716/` 下的舊設計文件（`phase3_settings.diff` 等）與本次實際部署已有出入（未採用 `SubagentStart`／完整六 hook 集、`session-policy.json` 的 `mirror_rules` 仍是空的未實作）——該資料夾屬 outputs 過程稿，未回頭同步修訂，之後有人接手需留意別直接照舊文件二次部署。
- Windows 端設定檔尚未套用本次 PreToolUse／Stop 接線（本次只動本機 Mac，設定檔非跨機同步檔案）。
- **2026-08-05 補充回報**：另一 session（於 ody 分工機制任務中）複驗時回報環境雜訊——`postread` hook 每次 `Read` 後都報 `generation.json` 缺檔錯誤，屬本節「建議找機會開新 session 實跑驗證」那條的具體命中案例。本 session 未深入診斷（`wtf-config/hooks/wtf-session-gate.py` 本身受 `protected()` 擋下直接 Read/Bash 讀取，且與當次任務無關），僅記錄待後續專門處理。
