# TaskLog 2026-09-16 — wtf-session-gate 死鎖修復（ai-team：三輪討論＋三方輪流驗收）

> Tech Lead：Claude@comaMacBookAir（session `claude_wtf`）。執行層：Codex（headless exec，唯讀）、Antigravity（agy --print）、ch06（Claude session，事故 2 當事人）。PO：三藏。
> 狀態：**三方最終驗收全 GO；2026-09-17 session-end 依指令 commit。** 延後四項（flock、活躍 bundle 禁刪、額度改 PostToolUse 扣、hook 指向已驗證版本目錄）仍待 PO。 hook 直指 repo，工作區版本已即時生效於本機所有 session。

## 事故
1. **文件主控 session**：cwd 在 Drive，Finder 改名搬移後 FileProvider 重建 inode → getcwd EPERM → gate 對相對字串 resolve 撞 getcwd → 每次工具呼叫全域 deny，訊息只有 errno；sync 逐專案讀 AGENTS.md 未隔離整支崩。
2. **HsinchuSEC ch06 session（105 次 deny）**：harness 沒發 InstructionsLoaded，靠補讀拿收據；resume 換代後再補讀被「連續兩代靠補讀→熔斷」永久拒絕，唯一復原路徑被擋，喊停也被 Stop hook 擋。

## 已 commit（PO 授權前的止血，07fce0d／bde839e／4406b74）
canonical() 不依賴 cwd；sync 逐專案隔離；移除連續代熔斷並自動解除舊熔斷；deny 訊息附 tool 與路徑。

## 本輪未 commit 的 diff（wtf-config/hooks/wtf-session-gate.py＋tests/test_session_gate.py，514 行）
- **Codex 第 1 輪抓到我引入的回歸**：canonical() 改不 resolve 相對字串後，protected() 的 commonpath 對相對／絕對混用拋 ValueError、`continue` 把子字串檢查一起跳過 → 含受保護路徑的 Bash 指令文字漏攔。修：兩道檢查分離；相對路徑用事件 cwd（非 getcwd），無 cwd 保守擋；MCP 工具（mcp__）path 類鍵不做檔案系統解析（ch06）。
- describe_failure 對非 dict tool_input 二次崩潰＝hook exit 1＝fail-open（Codex）→ 防崩；非 dict tool_input → protected() 保守擋。
- 補讀額度每代每檔 1→3 次（PreToolUse 先扣、Read 被別的 hook 擋會白燒；Codex／ch06）。
- deny／block 訊息帶原因碼 RECEIPT_MISSING／FUSE_TRIPPED＋每檔剩餘次數＋復原命令（ch06）；舊熔斷判為 legacy_fuse，訊息叫人 Read（自癒）而非另開 session（Codex 第 2 輪指出矛盾）。
- Stop：熔斷、狀態損壞、bundle 消失、recovery 形狀錯 → 放行結束＋盡力稽核；identity 錯誤仍 block（Codex）。
- 狀態 JSON 損壞／形狀錯 → 隔離改名 .corrupt-<ts>，下次可重建；bundle／manifest 絕不隔離（ch06、Codex）。
- 新增唯讀 `doctor` 子命令（`python3 <hooks>/wtf-session-gate.py doctor <session_id>` 或 stdin JSON）：不改狀態（QUARANTINE_ENABLED 關）、不依賴 cwd、逐項容錯、排在 BYPASS 稽核之前。
- 測試 29→50：死 cwd、Bash 文字含受保護路徑、相對路徑對事件 cwd、MCP 豁免、非 dict、連續代補讀可通、3 次後熔斷、舊熔斷解除、熔斷後 Stop 放行、狀態損壞 Stop 放行＋畸形事件仍 block、recovery 損壞／形狀錯自癒、doctor 唯讀（含 BYPASS）、事故 2 全鏈。全套 50 通過。

## 討論紀錄（摘要，原文在 session scratchpad aiteam/round*.txt）
- R1：Codex 抓 protected() 回歸＋describe_failure 崩潰＋既有測試名不符實；agy 提 bundle 刪除／JSON 損壞／flock／doctor；ch06 提原因碼、餘額、Stop 放行、額度時機。
- R2：agy GO（其 L333 指摘經查非 bug：directory.parent.name＝session id）；Codex FAIL（Stop 在狀態損壞時仍 block、舊熔斷訊息矛盾、非 dict、doctor 容錯與 BYPASS 唯讀、占位路徑）；ch06 條件 GO（MCP 豁免、JSON 隔離、全鏈測試）。全部處理。
- R3：agy GO、ch06 GO；Codex NO-GO（doctor 經 read_json 觸發隔離違反唯讀；recovery used=null 落在放行捕捉外）→ 修（隔離開關、load_recovery 形狀驗證、cmd_stop 全包）＋2 測試。最終：Codex GO、agy GO、ch06 GO。

## 延後（交 PO 決定，非本輪必做）
- flock 鎖（同 session 並行換代／補讀）；活躍 bundle 禁刪（sync 清理前查 generation.json 引用）；補讀額度改 PostToolUse 成功才扣；hook 改指向已驗證版本目錄而非 repo 工作區（改檔即全機生效的風險本輪親身經歷：R1 的回歸在 commit 前已影響所有 session）。

## 待辦
- [x] session-end commit＋push（2026-09-17）（訊息草稿：「gate：ai-team 三輪審查後修法——protected 回歸、Stop 不卡、狀態隔離、doctor、50 測試」）
- [x] 教訓寫入 lessons-learned（本輪：改 protected() 必配 Bash 文字＋相對路徑測試；hook 直指工作區＝未 commit 也生效）
