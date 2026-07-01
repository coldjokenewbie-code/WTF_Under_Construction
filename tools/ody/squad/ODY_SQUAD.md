# 奧德賽小隊（ody）— 編組與規則
> 籌備：2026-07-02｜精神：Odysseus（多謀善變、從經驗學）＋Tyrion（謀略、識人、守分寸）
> 設計源：`_context/Plan_2026-07-01_discipline-harness.md`（三道閘＋教練制）

## 根本問題
規範停在 prompt 層、無輸出前檢查＝靠 AI 自律必漂移。
**解＝結構強制**：hook 機器攔截＋錯誤轉可機檢規則（越用越會擋，複利）。

## 編組（4 角色，可由 Claude/Codex/Antigravity 動態擔任）
| 角色 | 職責 | 落地件 |
|---|---|---|
| **Odysseus**（策略/執行） | 拆任務、判風險、增量實作；**動工前立契約** | `coach.py new` |
| **Tyrion**（輸出守門） | 交付前 lint：禁詞/過長，違規退回重寫 | `reply_lint.py`＋`stop_hook.py`（Stop hook，2026-07-02 實戰攔截驗證✅） |
| **Verifier**（驗收） | 宣稱完成→獨立機檢＋逐條核證據；**禁自驗自過** | `coach.py check`＋subagent `.claude/agents/ody-verifier.md`；跨 AI 用 `codex exec`/`agy --print` |
| **Mentor**（學習） | 每次糾正/FAIL → 轉一條可機檢規則，下次自動擋 | `coach.py add-rule`→`coach_rules.json`；輸出樣式→`lint_rules.json` |

## 三道閘（每個任務）
1. **接任務→立契約**：`coach.py new <id> --goal --scope --accept [--verify-cmd] [--permission]`。
   scope allowlist＋逐條驗收標準＋授權點（開工前向 PO 一次講定）。**無契約不動工**。
2. **宣稱完成→機檢驗收**：`coach.py check <id>`——契約完整／scope 越界（diff 比對 allowlist，開工前既髒檔豁免）／自驗證據逐條（cmd 須 exit 0；note 禁空話）／handoff ≤60 行／verify_cmds 全過／**coach_rules 全套用**。FAIL 即退回。
3. **每次留紀錄→FAIL 轉規則**：事件入 `data/events.jsonl`（contract_created/evidence_added/coach_check/rule_added）；重複同型錯誤 → Mentor `add-rule`。

## 自評＋學習雙迴圈（複利）
```
輸出層：糾正 → lint_rules.json 禁詞/門檻 → Tyrion Stop hook 下次自動擋
工作層：FAIL → coach_rules.json 可機檢規則 → Verifier check 下次自動套用
```
- 學習＝**新增可機檢規則**，不是寫心得。無法機檢者降為 checklist 由 Verifier 人工核。
- 成本層另有 `ody/learn.py`（events 算省 API 指標＋升級草案）。

## 最小可落實規則（生效中）
1. 回應結論先行、禁聊天語氣/浮誇/功勞詞（Tyrion 硬擋）、散文 ≤500 字。
2. 未要求不主動改碼/開計畫；授權前置一次講定。
3. 犯錯即停工：先 Mentor 加規則才續。
4. 視覺分只看實圖；禁盲評。
5. 禁自驗自過：驗收換另一 context（subagent）或另一 AI（headless CLI）。
6. 保護路徑（全域設定/settings）未經 PO 明授不得入 diff（coach R001）。

## 用法速查
```bash
python3 tools/ody/squad/coach.py new <task_id> --goal "..." --scope "glob" --accept "標準" ...
python3 tools/ody/squad/coach.py evidence <task_id> <編號> --cmd "驗證命令"   # 或 --note
python3 tools/ody/squad/coach.py check <task_id>          # PASS/FAIL
python3 tools/ody/squad/coach.py add-rule --rule-id R00x --type ... --msg ...  # Mentor
echo "回覆草稿" | python3 tools/ody/squad/reply_lint.py    # Tyrion 手動自評
```

## 狀態（2026-07-02）
- Tyrion Stop hook：已掛 settings.local.json 並**實戰攔截驗證**（引文誤攔為已知型態，待加引文白名單）。
- 三道閘 MVP：coach.py＋coach_rules.json（R001 保護路徑、R002 證據禁空話）＋Verifier subagent 已建。
- 跨工具：Codex/Antigravity 無原生 hook → 規則進 CODEX.md/GEMINI.md 開場必載＋輸出前自跑 reply_lint；**待 Claude 端驗穩後推全域**。
- 下一步：PreToolUse 契約閘（無契約擋 Write/Edit，opt-in）、跨 AI coach 接線、nightly 聚合高頻違規。
