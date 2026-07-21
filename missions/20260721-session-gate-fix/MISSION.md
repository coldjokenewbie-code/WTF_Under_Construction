# MISSION：session-gate-fix

## 方向（一句話）
修好 wtf-session-gate 當代故障：先止血讓 `cmd_postread` 不再硬崩，再把 settings.json 的 `WTF_BUNDLE_SHA256` 納入 SSOT 自動同步與四方機檢，從根因杜絕 bundle 換代後的 SHA 漂移，全部在 repo 內以純函式＋測試完成。

## 背景（規劃棒查證，不必重查）
- 診斷全文：`_context/TaskLog_2026-07-21_session-gate診斷.md`。
- `wtf-config/sync_config.py` 的 `deploy_session_bundle()`（86行）／`check_bundle_integrity()`（106行）是 2026-07-19 commit `33ecafc` 新增，已自動維護 `~/.claude/CLAUDE.md` 尾端 bundle import block 並做三方機檢（CLAUDE.md import SHA＝bundle 目錄名＝manifest digest）。**但完全沒碰 `~/.claude/settings.json`**——`SessionStart` hook 呼叫 `wtf-session-gate.sh init` 帶的 `WTF_BUNDLE_SHA256` 是寫死值，沒有機制隨 bundle 換代同步。`choose_bundle()`（`wtf-config/hooks/wtf-session-gate.py:61`）優先採用這個 env var 選 bundle 目錄，選錯→`generation.json` 綁死舊代→`InstructionsLoaded` 收據比對必敗→`cmd_postread()`（264行）撞進沒有 `path.exists()` 防禦的 `read_json(directory / "recovery.json")` 直接炸成 GateError。這就是使用者實際看到的報錯本體。
- 2026-07-19 前次研究（`outputs/ody-session-gate-headless-20260719/HEADLESS_DIAGNOSIS.md`）已定案：`PreToolUse`／`Stop` 維持觀察模式（未接線），未完成完整 canary 驗證前不恢復。本 mission 不重新裁決此問題。
- 規劃棒方法：兩個獨立 opus 子任務各出分解方案（部署原子性優先 vs 最小止血優先），第三個 fresh-context opus 比較擇優融合，裁決見下方「模糊標準錨點」。

## 模糊標準錨點
**正例（屬本棒）**
- `cmd_postread` 比照 `recovery_read`（225行）補 `recovery.json` 的 `path.exists()` 防禦，一般 Read 不再炸成 GateError。
- 把 settings.json `WTF_BUNDLE_SHA256` 自動同步邏輯寫進 `sync_config.py`（純函式＋fixture 測試，不碰真實 `~/.claude`）。
- `check_bundle_integrity` 由三方擴為四方（新增 settings.json 那一項）。

**反例（出界）**
- 在雲端 session 直接編輯使用者 `~/.claude/settings.json` 或執行 `sync`——本機才能做，只交付 repo 內程式碼＋HANDOFF 步驟。
- 順手接線 PreToolUse／Stop——2026-07-19 已定案維持觀察模式，本 mission 不重新裁決。
- 重寫 `choose_bundle` 選 bundle 演算法或 `wtf_bundle.py` 產生邏輯——根因在 settings.json env 未同步，不在選擇演算法本身。

## 硬底線（可機檢）
1. 重現故障情境（generation 綁舊 SHA、receipts 必缺、`recovery.json` 不存在）下，一般非復原 Read 的 postread 不再拋出「invalid JSON / No such file」型 GateError。
2. 止血後，非復原 Read 絕不誤寫任何 receipt（無 false-positive 收據）；合法 full-read 復原路徑仍正確寫收據（不回歸）。
3. `check_bundle_integrity` 在 settings.json 的 `WTF_BUNDLE_SHA256` ≠ 當代 SHA 時回報 STALE/False。
4. 跑 sync 邏輯後，settings.json 的 `WTF_BUNDLE_SHA256` 等於當代部署 bundle SHA（四方一致）。
5. 所有新程式為 pure function＋單元測試，測試以 `tmp` / `WTF_GATE_HOME` override，零網路、不碰真實 `~/.claude`。
6. `wtf-session-gate.py` 除 `cmd_postread` 單一防禦點外零改動；未接線 PreToolUse／Stop。
7. 全套 pytest 綠燈。

## Milestone（每個＝使用者簽核點）
1. **M1 止血**：`cmd_postread` 補 `recovery.json` 的 `path.exists()` 防禦＋回歸測試。
   驗收：重現情境下 postread 不再 hard-crash 且不誤寫收據；正常復原路徑不回歸；pytest 綠。可獨立簽核、獨立部署。
2. **M2 根因**（settings.json 納入 SSOT 自動同步＋四方機檢）：pure-function helper＋`check_bundle_integrity` 擴四方＋部署流程串接自動覆寫，全數 fixture 測試。
   驗收：給定含舊 SHA 的 settings.json fixture，跑 sync 邏輯後 `WTF_BUNDLE_SHA256` 被覆寫成當代 SHA；四方任一不符 check 回 STALE；pytest 綠。全程不需在使用者本機執行。
3. **M3 守門與文件**：lessons-learned 記錄根因鏈＋HANDOFF 列後續步驟。
   驗收：lessons-learned 有根因鏈條目；HANDOFF 明列「本機跑 sync＋重驗 canary」為交付後步驟。

## 邊界
- **禁改**：`wtf-session-gate.py`（除 `cmd_postread` 一處）、`session-policy.json`、manifest 結構、`wtf_bundle.py` bundle 產生邏輯、`choose_bundle` 選擇演算法。
- **不做**：不接線 PreToolUse／Stop（維持觀察模式）；不在雲端 session 修改使用者本機任何檔（`~/.claude/settings.json`、`~/.claude/CLAUDE.md`）、不執行 `sync`；不做完整 canary 驗證（列 HANDOFF）；不自動刪除使用者 bundle 目錄。
- **僅限 repo 內**：只交付 repo 內程式碼＋測試；「使用者本機執行 sync 才生效」為交付物之外的後續步驟。
