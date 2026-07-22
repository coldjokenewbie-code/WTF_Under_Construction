# TaskLog 2026-07-21：wtf-session-gate 故障診斷與修復

> 本機 session（Claude@comaMacBookAir.local）診斷完成，2026-07-22 使用者直接指示於當下 session 修復（跳過夜間棒排程），已修並驗證。

## 症狀
本 session 每次 `Read` 工具呼叫後，`PostToolUse:Read` hook 皆報錯：
```
wtf-session-gate: invalid JSON /Users/coma/.claude/wtf-session-state/<session>/main/recovery.json:
[Errno 2] No such file or directory: '.../recovery.json'
```

## 根因（三個問題疊加）

1. **Bundle SHA 沒跟著換代（主因）**
   `~/.claude/settings.json` 的 `SessionStart` hook 寫死
   `WTF_BUNDLE_SHA256=ba55340b81fe0b28a030a9a410a14dd093a1123008fe733fca7744fbfdcd5778`
   （呼叫 `wtf-session-gate.sh init`）。但本 session 實際由 CLAUDE.md `@import`
   載入的 bundle 是 `f736b127dbf7665cf1265e956396b163f75fa76f60c854e507d0700743a0721f`。
   `~/.claude/wtf-session-bundles/` 下同時存在 3 個不同 SHA 的 bundle 目錄
   （另一個是 `74d1db665db64bd874aff4f08867f1d7300ca55806a902adc83114144d6e143f`），
   代表 bundle 內容變更會重新產生 SHA，但 `wtf-config/sync_config.py` 全文搜尋
   不到任何寫回 `settings.json` 的邏輯——沒有機制在 bundle 換代時同步更新這個
   寫死的環境變數。結果本 session 的 `generation.json` 綁死在舊 bundle
   （`ba55340b...`）路徑上。

2. **InstructionsLoaded 收據因此從未寫成**
   GLOBAL.md/AGENTS.md 實際在新 bundle（`f736b127...`）底下被讀取，但
   `generation.json` 綁的是舊 bundle 路徑，`cmd_instructions()` 的路徑比對
   （`wtf-session-gate.py:174-177`）必然失敗（`matched` 長度為 0）→ 拋
   `GateError("InstructionsLoaded path is not a required bundle source")`。
   整個 session 沒有任何 `*.receipt.json` 被寫入 `main/` 目錄（已核對，
   `main/` 下只有 `generation.json`，無收據檔）。

3. **PreToolUse／Stop 兩個 hook 從未在 settings.json 註冊**
   查了 `~/.claude/settings.json`、`~/.claude/settings.local.json`（不存在）、
   專案內 `.claude/settings.json`／`.claude/settings.local.json`（皆為空 `{}`）——
   目前只掛了 `SessionStart(init)`、`InstructionsLoaded`、`PostToolUse:Read(postread)`，
   **完全沒有 PreToolUse 掛 `wtf-session-gate.sh pretool`，也沒有 Stop 掛
   `wtf-session-gate.sh stop`**（Stop hook 現掛的是 `tools/ody/squad/stop_hook.py`，
   不是 session-gate）。`pretool` 對應的 `recovery_read()`
   （`wtf-session-gate.py:215-242`）是唯一會在 `recovery.json` 不存在時安全給
   預設值 `{"schema":1,"used":{}}` 的地方；它沒被呼叫，`recovery.json` 就永遠
   不會被建立。

4. **`cmd_postread` 本身有防禦漏洞（次要，值得順手修）**
   `wtf-session-gate.py:264` 直接 `read_json(directory / "recovery.json")`，
   沒有像 `recovery_read()`（225 行：`read_json(path) if path.exists() else {...}`）
   一樣先判斷檔案是否存在。三個問題疊加下，每次 Read 只要收據缺失就會撞進這行，
   檔案不存在直接炸成 `GateError`，這才是使用者看到的報錯訊息本體。

## 實際影響（已確認，非猜測）
這套 fail-closed 收據閘從掛上後就沒真正生效過（PreToolUse/Stop 沒接線，
形同虛設）——**這次報錯只是把「一直沒生效」從靜默變成「一直在吵」，不是新
出現的保護缺口**。GLOBAL.md/AGENTS.md 內容有沒有送達不受此閘影響，那是
Claude Code 原生 `@import` 機制，跟這個閘完全無關。PostToolUse hook 是事後
執行，Read 結果已回傳給模型，報錯擋不了已完成的動作，純噪音（會持續佔用
對話 context）。

## 待修項目（建議修復順序）

1. **止血**：`wtf-session-gate.py` 的 `cmd_postread()`（264 行附近）比照
   `recovery_read()` 的寫法，讀 `recovery.json` 前先判斷 `path.exists()`，
   不存在則用預設值 `{"schema": 1, "used": {}}`，不要直接炸掉。
2. **修根因**：決定 bundle SHA 要如何跟 `sync_config.py sync` 保持同步——
   選項 (a) `sync_config.py` 新增邏輯，每次算出新 bundle SHA 後自動改寫
   `~/.claude/settings.json` 裡 `wtf-session-gate.sh init` 那行的
   `WTF_BUNDLE_SHA256=...`；或 (b) 該 hook 改成不吃寫死的 env var，改用
   `choose_bundle()` 既有的「目錄下只有一個候選就自動選」邏輯（`base.iterdir()`
   若只有一個 bundle 目錄則不需要 `WTF_BUNDLE_SHA256`）——但現況目錄下同時有
   3 個 bundle（可能含舊代未清），需先確認舊 bundle 該不該清、由誰清。
3. **決定是否要接上 PreToolUse／Stop**：這是設計原意（fail-closed 全套），
   但目前完全沒接線，形同半成品。需使用者決定：(a) 補接線讓這套閘真正生效
   （需先驗證 pretool/stop 邏輯不會誤擋正常工作流，建議先在單一機器 canary
   測試，呼應 `lessons-learned.md` 2026-07-17 條「session-gate canary 實測」
   的既有經驗）；(b) 或這套機制本來就還在實驗階段、先不接線，只留
   postread 記錄用——若選 (b) 則第 1 項止血後即可視為完成，不必做第 3 項。
4. 修完後，本機（Mac／Windows 皆需）跑 `sync_config.py sync` 重新部署，
   並開新 session 驗證 Read 不再報錯（hook 不熱載，需新 session）。

## 相關原始碼位置
- Hook 腳本：`wtf-config/hooks/wtf-session-gate.py`（335 行）、
  `wtf-config/hooks/wtf-session-gate.sh`（dispatcher）
- 註冊處：`~/.claude/settings.json`「hooks」段
- Bundle 目錄：`~/.claude/wtf-session-bundles/<sha>/`
- Session 狀態：`~/.claude/wtf-session-state/<session_id>/<agent>/`

## 背景
2026-07-17 lessons-learned 已有「session-gate canary 實測」條目，記錄
`--bare`／Stop hook block 次數上限／headless 復原通道等行為事實，屬同一套
機制的前次驗證。本次是該機制在**日常真實使用**中首次觀察到的故障，非刻意
canary 測試發現。

## 2026-07-22 修復（Claude@Mac，當下 session 直接執行，非夜間棒）

1. **止血**（`cmd_postread`，`wtf-session-gate.py`）：`recovery.json` 讀取前加
   `path.exists()` 判斷，不存在則用預設值 `{"schema": 1, "used": {}}`，比照
   `recovery_read()` 既有寫法。不再對缺檔直接拋 `GateError`。
2. **修根因**（bundle SHA 過期）：`choose_bundle()` 新增第三順位來源
   `bundle_sha_from_claude_md()`——直接讀 `~/.claude/CLAUDE.md` managed import
   block 裡的 SHA（`sync_config.py` 每次 sync 都會自動改寫這行，是唯一真正
   跟著換代的權威來源）。優先序：event 欄位 > `WTF_BUNDLE_SHA256` env var（手動
   覆寫用）> CLAUDE.md import（新增，日常自動跟代）> 單一候選目錄自動選
   （bootstrap 邊界情況）。
   同時清掉 `~/.claude/settings.json` SessionStart init hook 裡寫死的
   `WTF_BUNDLE_SHA256=ba55340b...` 環境變數（否則會蓋掉新邏輯，繼續讀舊
   SHA）——**僅改本機（Mac）settings.json，Windows 端未同步，需另外處理**。
3. **驗證**：sandbox（`WTF_GATE_HOME` 指向 tmp dir、複製 bundle＋CLAUDE.md）
   跑 `init → instructions(GLOBAL.md) → instructions(AGENTS.md) → postread`
   全流程，四步皆 exit 0、兩張收據正確寫入、postread 對後續一般 Read 安靜放行
   （無 GateError）。`python3 -m py_compile` 過。
4. **PreToolUse／Stop 接線**：問過使用者，**選擇先不接**（fail-closed 尚未
   canary 測試，維持現況只記錄不擋；待辦見下）。
5. **本 session 仍會看到殘留報錯**：本 session 的 `generation.json` 已在
   session 開始時綁定舊 SHA（`ba55340b...`），修復不熱載，需開新 session 才
   會用到新邏輯——已知現象，非修復失敗。

## 待辦（結案後仍留）
- Windows 端 `~/.claude/settings.json`（或對應路徑）若同樣寫死
  `WTF_BUNDLE_SHA256`，需手動比照本次做法移除（下次 Windows session 處理）。
- PreToolUse／Stop 是否接線＝獨立待決，需先 canary 測試才能評估風險。
- `~/.claude/wtf-session-bundles/` 下 3 個舊 bundle 目錄未清理（非阻塞，本次
  CLAUDE.md fallback 已繞開此問題，不影響修復有效性）。
