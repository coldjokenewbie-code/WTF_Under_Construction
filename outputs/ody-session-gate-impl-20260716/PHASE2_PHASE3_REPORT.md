# 階段 2（隔離 canary）＋階段 3（影子部署）報告 [Claude@Mac] 2026-07-16

> 契約：`wtf-session-gate-impl-20260716`｜環境：Claude Code 2.1.210, macOS
> canary 位置：session scratchpad `gate-canary/`（logs 全留存）；隔離方式見 `CANARY_NOTES.md`（暫存專案＋`--setting-sources project`，不偽造 HOME）

## 階段 2 實測結果

| # | 待驗項（PROPOSAL 未證實清單） | 結果 | 證據 |
|---|---|---|---|
| 1 | `InstructionsLoaded` 是否實發 | **實發**。每個 `@import` 各一筆（`load_reason=include`）＋CLAUDE.md 本體一筆（`session_start`） | `logs/InstructionsLoaded.jsonl` |
| 2 | `parent_file_path` 是否存在 | **存在**（網頁文件未載，實機有）——指向 import 它的 CLAUDE.md；feature-detect 設計正確，canary 中 `parent_check=matched` | 同上＋收據檔 |
| 3 | 專案內相對 import 是否載入 | **載入**。無工具情況下模型答對 GLOBAL 版控鐵律副檔名白名單（內容確在 context） | run 1 輸出 |
| 4 | 專案外絕對路徑 import | **不載入**（headless 未經核准即靜默略過，模型只看到字面 `@...`）。user 層 `~/.claude/CLAUDE.md` 同目錄相對 import 是否免核准＝**階段 4 首要測項（互動式觀察核准視窗）** | run 0 探測 |
| 5 | 快樂路徑：收據自動成立＋工具放行 | **PASS**。開場兩張收據由 loader 事件簽收（非 Read 復原），Write 放行、sentinel 產生、Stop 通過，未觀察到競態誤擋（單樣本） | run A；收據檔 `load_reason=include, parent_check=matched` |
| 6 | fail-closed：無 import 時全擋 | **PASS**。Write/Bash/Read（非授權路徑）全被 deny，sentinel 未產生，收據零張 | run B/C/D |
| 7 | Stop 連續 block 上限（先前兩 AI 互相背書的「8 次」） | **2.1.210 實測連續 block 9 次仍有效**，session 由 `--max-turns` 終止——「8 次強制放行」在本版不成立（進一步證偽 agy 捏造引文） | run D `Stop.jsonl` 9 筆 |
| 8 | Read 復原通道 | 機制經 17 項單元測試（含一次性額度、連續復原熔斷）；**實模型採用率 0/3**——即使 deny/Stop 訊息附完整路徑與指令，headless 模型多半不走復原、反覆嘗試原任務至 max-turns。復原屬維修通道，保證仍由 fail-closed 承擔；正式部署建議 SessionStart 注入一段簡短指引降低卡死率 | run B/C/D 工具序列 |
| 9 | `--bare` 旁路 | 本機 `--help` 明載 skip hooks＋CLAUDE.md auto-memory ＝ 整組保護一起關（同時 OAuth/keychain 不讀，僅 API key 可用，實用面窄）。列入已知旁路，與 `disableAllHooks` 同級 | CANARY_NOTES.md |

### 過程中修正的三個實作缺陷（單元測試 17/17 全程保持綠燈）
1. `postread` 在收據齊全時對一般 Read 誤報錯誤 → 改安靜放行。
2. parent 期望路徑寫死 gate home → 增 `WTF_GATE_PARENT` 環境變數覆寫。
3. deny／Stop 訊息只列檔名 → 補完整 bundle 路徑＋可執行指令（提升復原可達性；成效見第 8 項，誠實記錄）。

### 未測項（遞延，不影響本輪驗收）
compact 重簽（headless 難觸發）、subagent 收據隔離（SubagentStart 實測）、Windows 平台、token/延遲量測（10 session 統計）、user 層 import 核准行為（階段 4 第一步）。

## 階段 3 影子部署結果

- 正式 `~/.claude/wtf-session-bundles/ba55340b…/` 已建（附加性；GLOBAL 10,213B＋AGENTS 6,957B＋manifest）。
- `phase3_settings_merged.dryrun.json`＋`phase3_settings.diff`（68 行）＝**擬議** settings 變更，供核准點 3 審查；Stop 走 `stop_dispatcher.py` 合併既有 ody lint。
- `phase3_claudemd_import.proposed.txt`＝擬議 CLAUDE.md 附加兩行。
- `phase3_baseline_hashes.txt` vs `phase3_after_hashes.txt` diff 為空：**正式 settings.json 與 CLAUDE.md 全程未動** ✓

## 待 PO（核准點 3）

審 `phase3_settings.diff` 與擬議 import 兩行後，明授才進階段 4（改正式 settings＋CLAUDE.md、先跑互動式 import 核准觀察、單機限時啟用）。
