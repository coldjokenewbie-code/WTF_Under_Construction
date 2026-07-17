# 第二輪核驗紀錄：DESIGN 技術事實三方對照＋裁決

> 三方：agy（`/tmp/agy_challenge2.log`）、claude-code-guide subagent（官方文件檢索）、Claude 直接 WebFetch https://code.claude.com/docs/en/hooks（第一手，2026-07-15）
> 裁決原則：第一手文件 > 兩個轉述；轉述互相矛盾時必查第一手

## 技術事實對照表

| # | DESIGN 宣稱 | agy | guide | 第一手裁決 |
|---|---|---|---|---|
| 1 | InstructionsLoaded 存在＋欄位 schema | CONFIRMED（含 parent_file_path） | PARTIAL | **大部成立**：事件存在，input 含 session_id/file_path/load_reason，load_reason 有 include/compact（另有 session_start/nested_traversal/path_glob_match）。**parent_file_path 文件未載**——DESIGN 的收據驗證依賴此欄，須改為存在才驗、缺欄不擋（feature-detect） |
| 2 | SubagentStart 存在 | CONFIRMED | CONFIRMED | 成立（事件清單第 13 項） |
| 3 | user CLAUDE.md @import＋launch 展開＋外部 import 首次核准 | CONFIRMED | CONFIRMED | 成立 |
| 4 | permissionDecision deny／exit 2 擋、exit 1 不擋 | CONFIRMED | PARTIAL | 成立（deny 明載；exit 2＝Blocking error；exit 1＝non-blocking continue） |
| 5 | **Stop 連續 8 次 block 後強制結束** | CONFIRMED（附「原句」引文） | REFUTED | **REFUTED——官方文件無此文字**。agy 引用的英文句在文件中不存在（引文來源不明或捏造）；Codex 殘餘風險 3 的「官方明載」同樣不實。實際安全閥行為未知，須部署 canary 實測，不得引為已知數 |
| 6 | shell:bash／disableAllHooks／--bare 跳過 hooks | CONFIRMED | PARTIAL | shell、disableAllHooks 成立；**--bare REFUTED**：官方定義為 minimal mode（skip auto-discovery），非跳過 hooks |

## 對抗品質裁決

1. **agy 第 5 項引文捏造**：agy 逐字「引用」了官方文件不存在的句子（"overrides the hook and ends the turn after 8 consecutive blocks"）為 Codex 的宣稱背書。兩個 AI 對同一條未經證實的敘述互相「確認」＝迴聲室效應實例；且 agy 自己的第 3 大質疑（8 次擊穿）建立在這條捏造引文上。
2. **agy 5 大有效性質疑中 4 條是重新包裝**：同權限竄改（=DESIGN 殘餘風險 9，Codex 已明言 user hook 非防竄改邊界）、非同步競態（=風險 4）、Stop 上限（=風險 3，且前提未證實）、Explore/Plan 限制（=風險 10）。把設計已自認的保證邊界當「方案不成立」的論據，屬過度裁決。
3. **agy 實質新貢獻 2 條**：(a) token 死循環風險（Read 復原 20KB→context 膨脹→compaction→收據重簽→再 Read），需要緩解設計；(b) 抓到 Codex stdout 宣稱「已通過 ody 獨立複驗」不實——`tools/ody/data/events.jsonl` 本契約僅 2 條 contract_created，無任何 check 紀錄。
4. **Codex 不實宣稱屬 ody 閘2 違規型態**（宣稱完成/已驗無證據），已要求修訂版移除，並由本輪真正的 coach check＋ody-verifier 補上程序。

## 對 DESIGN 的修訂要求（交 Codex 出 PROPOSAL.md）

R1. 收據驗證中 parent_file_path 改 feature-detect（有則驗、無則不以此擋），標註「文件未載欄位」。
R2. 刪除「Stop 8 次上限」作為已知數的所有引用；改為「安全閥行為未知，canary 實測項目」，並重估 Stop 閘的保證強度敘述。
R3. --bare 敘述更正為 minimal mode；防竄改敘述只保留 disableAllHooks 與同權限編輯兩條真實旁路。
R4. 回應 token 死循環質疑：給出緩解（如 compact 後 load_reason=compact 事件本身即可重簽收據、Read 復原僅限 loader 異常一次性、連續復原次數告警）。
R5. 刪除任何「已通過複驗」宣稱；驗收狀態以 events.jsonl 為準。
