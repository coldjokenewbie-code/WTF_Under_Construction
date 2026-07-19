# 階段4 收尾修復報告 [Claude@Mac] 2026-07-19

> 契約：`wtf-session-gate-headless-20260719`｜Claude 接手（codex headless 長輸出卡死，見 lessons）
> 狀態：修復完成、canary 通過；待 agy 質疑＋ody-verifier 複驗＋PO 恢復強制

## 修了兩個問題

### 1. 根因：import 手改被 sync 洗掉 → 改由 sync 自動維護
`sync_config.py` 新增 `deploy_session_bundle()`：每次部署 CLAUDE.md 後，自動產生/確認 bundle 並在 CLAUDE.md 尾端寫入當代 SHA 的 managed import block（`# >>> WTF-SESSION-BUNDLE >>>`…`<<<`）。從「sync 洗掉 import」反轉為「sync 維護 import」。
- `check` 加機檢 `check_bundle_integrity()`：CLAUDE.md import SHA ＝ bundle 目錄名 ＝ manifest digest ＝ 與當前 SSOT 內容一致，四者任一不符即 STALE/BROKEN 且 check 非零。
- `check_claude_dir` 比對改為「去掉 managed block 後的本體 == SSOT」，不因 block 誤判 STALE。

**實測**：
- sync → CLAUDE.md 出現 block、SHA=ba55340b…，18 專案 AGENTS.md／skills／codex／gemini 部署不回歸。
- 冪等：重跑 sync，block 仍單一組（grep WTF-SESSION-BUNDLE = 2）。
- SSOT 改動 → SHA 自動更新（ba55→4f4a）；還原 → SHA 回 ba55。
- check exit 0，機檢行「session bundle import SHA/manifest/SSOT 三者一致」。

### 2. 並行競態：headless 兩個 InstructionsLoaded 搶建 generation → 收據不穩
canary 初測發現 headless 收據簽成不穩（0／1／2 都出現）。根因：`cmd_init` 與兩個 `cmd_instructions` 事件並行，各用「先查不存在再寫」建 `generation.json`、os.replace 互相覆蓋，產生不同 generation id，使部分收據對不上而失效。
- 修法：新增 `create_generation()` 用 **O_EXCL 原子創建**——並行時只有一個建成、其餘讀既有共用同 generation；只有明確旋轉（`source in {resume,compact,compaction,clear}`）才覆蓋。`cmd_instructions` 自建時 bundle 由事件 file_path 推導（不靠 choose_bundle，避免多 bundle ambiguous）。

**實測**：canary user-only 連跑 5 次，**每次穩定 2 收據、皆 load_reason=include（自動簽成，非 recovery、非鎖）**。

## 驗證總覽
- `test_session_gate.py`：20 項全綠（原 19＋新增 startup-不旋轉；並行自建 test_instructions_before_init 涵蓋競態）。
- canary user-only：5/5 穩定 2 收據 include。
- sync/check：冪等、機檢、不回歸皆通過。

## 誠實標註（未做／未測）
- **both（user+project 同時 import）格未實機測**：user-only 已 5/5 穩定，project-only codex 階段2（2.1.210）已驗；O_EXCL 對任意並行數安全（機制涵蓋），但 both 未跑實機 claude -p。列為殘餘未測。
- 孤兒 bundle GC：本次手動清了 canary 產生的 4f4a；自動 GC（30 天）未實作。
- 尚未 agy 對抗質疑、未 ody-verifier 複驗、未恢復 PreToolUse 強制（PO 手動）。

## 恢復強制前置條件（給 PO）
1. `sync_config.py check` exit 0 且機檢三者一致 ✓（已達成）
2. agy 質疑＋ody-verifier 複驗 PASS（進行中）
3. PO 執行恢復指令（見 RESUME.md 第5步）
恢復後若異常：`cp ~/.claude/settings.json.pre-observe.<最新> ~/.claude/settings.json` 即回觀察模式。
