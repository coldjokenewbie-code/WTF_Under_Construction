# 奧德賽小隊（ody）— 編組與規則
> 籌備：2026-07-02｜ai-team 三方（Claude lead＋Codex＋Antigravity）討論收斂
> 精神：Odysseus（多謀善變、從經驗學）＋Tyrion（謀略、識人、守分寸）

## 根本問題（先解，否則其他免談）
規範停在 prompt 層、**無輸出前檢查**＝靠 AI 自律必漂移（實測：Claude 一再違反「極簡/禁聊天語氣」，需使用者重複提醒、無複利）。
**解＝結構強制**：輸出守門 lint（機器攔截）＋錯誤轉可機檢規則（越用越會擋）。

## 編組（4 角色，可由 Claude/Codex/Antigravity 動態擔任）
| 角色 | 職責 |
|---|---|
| **Odysseus**（策略/執行） | 拆任務、判風險、決定誰做、增量實作 |
| **Tyrion**（守門 Gatekeeper） | 交付前 lint：禁詞/過長/結論先行，違規**退回重寫**（`reply_lint.py`） |
| **Mentor**（學習） | 每次糾正/錯誤 → 轉成 `lint_rules.json` 一條可機檢規則，下次自動擋 |
| **Verifier**（驗收） | 對照需求/diff/測試/截圖；**禁自驗自過**，驗收換另一 agent |

## 最小可落實規則（今日生效）
1. **回應**：結論先行、**禁聊天語氣/浮誇/功勞詞**（Tyrion 硬擋）、散文 ≤500 字。
2. **未要求不主動**：不擅自讀寫檔、改碼、開計畫。
3. **犯錯即停工**：被糾正 → 先由 Mentor 寫一條 `lint_rules.json` 規則 → 才續。
4. **授權前置**：需授權點開頭一次講定，過程不中途要權限。
5. **視覺分只看實圖**：禁用看不到圖的 agent 盲評當分數。
6. **禁自驗自過**：驗收換另一 agent。

## 自評 + 學習機制（複利）
```
違規/錯誤 → Mentor 轉成「可機檢規則」(regex/門檻/禁詞) 寫入 lint_rules.json
        → Tyrion 下次輸出自動套用 → 同類錯誤再也過不了關（不再犯）
```
- 學習＝**新增 lint 規則/checklist**，不是寫反省心得。
- 無法機檢者降為 checklist，由 Verifier 人工核，不進硬擋。

## 落地元件（本目錄）
- `reply_lint.py`：守門引擎（禁詞＋字數）。手動自評：`echo "文字" | python3 reply_lint.py`。
- `lint_rules.json`：規則庫（Mentor 維護；學習載體）。
- `stop_hook.py`：Claude Code Stop hook，交付前自動 lint、命中禁詞即 block 重寫（防迴圈＋fail-open）。**待使用者授權掛入 settings。**
- `ODY_SQUAD.md`：本檔。

## 狀態
- 引擎＋規則＋hook 已建並測過（禁詞 block、好放行、防迴圈、fail-open）。
- **待授權**：把 Stop hook 掛入 `.claude/settings.local.json`（classifier 擋自我修改，需明授）→ 掛上後守門即強制生效。
