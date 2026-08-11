# 階段 2 canary 前置探查 [Claude@Mac] 2026-07-16

## 本機環境事實（第一手，claude --help 實測）

- 版本：Claude Code 2.1.210
- **`--bare` 本機定義：「Minimal mode: skip hooks, LSP, plugin sync, attribution, auto-memory, background prefetches, keychain reads, and CLAUDE.md auto-discovery」——明寫 skip hooks**。
  - 與 VERIFY_ROUND2 依官方網頁文件判的「僅 skip auto-discovery、非 hooks 旁路」不符；以本機執行檔行為為準，`--bare` 應列入 hooks 旁路清單（修正 PROPOSAL 殘餘風險 7 的表述）。
  - 附帶：`--bare` 同時 skip CLAUDE.md auto-memory——@import 交付在 --bare 下也不生效，故 --bare 是「整組保護一起關」，與 disableAllHooks 同級旁路，偵測方式相同（收據不存在＝該 session 不受保護，canary 記錄之）。
- `--settings <file-or-json>`：可載入額外 settings；`--setting-sources user,project,local`：可指定只載哪幾層。
- 無 `CLAUDE_CONFIG_DIR` 相關旗標。

## 階段 2 隔離策略（取代偽造 HOME）

偽造 HOME 會斷 OAuth/keychain 認證。改用：
1. 暫存專案目錄 `canary-proj/`：放 `.claude/settings.json`（註冊七種 gate hooks）＋`CLAUDE.md`（@import 指向專案內 bundle 副本，相對路徑）。
2. 執行 `cd canary-proj && claude -p "..." --setting-sources project`——排除 user 層設定，避免正式機的 wtf-sync／ody Stop hook 干擾；認證走正常 keychain。
3. gate 的 state/bundle 路徑用 `WTF_GATE_HOME` 環境變數指到暫存目錄，不碰正式 `~/.claude`。
4. InstructionsLoaded 探測：hook 先接一個「把 stdin JSON 逐行落檔」的記錄器，直接觀測事件是否實發、欄位長怎樣（含 parent_file_path 有無）。
