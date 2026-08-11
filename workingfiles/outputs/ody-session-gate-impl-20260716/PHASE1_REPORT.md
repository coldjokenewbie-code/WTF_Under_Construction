# Session Gate 階段 1 報告

日期：2026-07-16  
契約：`wtf-session-gate-impl-20260716`  
範圍：離線實作與單元測試

## 實作摘要

- `wtf_bundle.py`：逐 byte 複製 GLOBAL／AGENTS，產生內容定址、不可就地覆寫的 bundle；manifest 記錄 schema、SHA-256、bytes、lines，支援假 HOME 與來源上限。
- `wtf-session-gate.py`：實作 session／agent generation、獨立原子收據、InstructionsLoaded 驗證、PreToolUse fail-closed、完整 Read 單次復原、PostToolUse 補收據、連續 generation 熔斷、Stop／SubagentStop 重驗、保護路徑與 bypass audit。
- `wtf-session-gate.sh`：依序尋找 `python3`、`python`；兩者皆無時 stderr 說明並 exit 2。
- `stop_dispatcher.py`：依序執行 session gate 與 ody Stop hook，合併所有 block；不讓 ody 因 `stop_hook_active` 提前放行。
- `session-policy.json`：schema v1、required sources、bytes／lines 上限與階段 4 mirror 規則 TODO。
- `test_session_gate.py`：17 項 tempfile 假 HOME 測試，未讀寫正式 `~/.claude` gate state／bundle／settings。

本階段未修改 `sync_config.py`，未安裝 hook，未修改正式 `~/.claude/settings.json` 或 `~/.claude/CLAUDE.md`。

## 測試命令與輸出全文

環境：macOS，Python 3.14.6。

```console
$ python3 -m unittest discover -s wtf-config/tests -p 'test_session_gate.py'
.................
----------------------------------------------------------------------
Ran 17 tests in 1.546s

OK
```

另執行：三個 Python 模組 `py_compile`、wrapper `sh -n`、policy `python3 -m json.tool`，皆 exit 0。`wtf-session-gate.py` 300 行，未超過 Quality Guard 上限。

## 已知限制

1. `InstructionsLoaded`、Subagent 欄位、compact 時序與 Stop 連續 block 行為尚未經隔離 canary；本報告不宣稱正式 Claude Code 相容性。
2. 多 bundle 並存時，階段 4 整合須由 hook input 的 `bundle_sha256` 或 `WTF_BUNDLE_SHA256` 指定現行 bundle。
3. `mirror_rules` 依需求維持空陣列；階段 4 才由 `projects-registry.md` 生成並接上 policy enforcement。
4. 本階段只證明離線狀態機與檔案驗證行為；不證明模型閱讀、理解或遵守自然語言設定。
5. bypass 與同 OS 權限修改仍是提案承認的維修／竄改邊界；audit 只留證，不構成安全邊界。
6. 未執行或宣稱 ody 獨立複驗；該步由本輪後續流程另行執行。
