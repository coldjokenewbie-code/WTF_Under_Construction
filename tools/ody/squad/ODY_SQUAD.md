# 奧德賽小隊（ody）— 編組與規則
> 籌備：2026-07-02｜精神：Odysseus（多謀善變、從經驗學）＋Tyrion（謀略、識人、守分寸）
> 設計源：`_context/Plan_2026-07-01_discipline-harness.md`（三道閘＋教練制）

## 根本問題
規範停在 prompt 層、無輸出前檢查＝靠 AI 自律必漂移。
**解＝結構強制**：hook 機器攔截＋錯誤轉可機檢規則（越用越會擋，複利）。

## 分工（2026-08-05：從口號變落地件）
以前「4 角色可由不同 AI 動態擔任」只是敘述，程式沒有實際派工機制——併入 ai-team 的分工能力後，`coach.py assign` 可把父契約拆給多個執行者各自領子契約獨立做，`coach.py check` 驗收父契約前會強制所有子契約已各自 PASS。跟 ai-team 的差異：ai-team 靠「討論輪數＋輪流驗收」流程約定把關，這裡靠契約鏈結構強制（缺子契約或子契約未過，父契約機檢直接 FAIL）。

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
python3 tools/ody/squad/coach.py check <task_id>          # PASS/FAIL（父任務會先查子任務全過）
python3 tools/ody/squad/coach.py assign <父task_id> <子task_id> --agent codex --goal ... --scope ... --accept ...  # 分工
python3 tools/ody/squad/coach.py children <父task_id>      # 查子任務現況
python3 tools/ody/squad/coach.py add-rule --rule-id R00x --type ... --msg ...  # Mentor
echo "回覆草稿" | python3 tools/ody/squad/reply_lint.py    # Tyrion 手動自評
```

## 狀態（2026-08-05 更新）
- 分工機制上線：`coach.py assign`/`children` ＋ `cmd_check` 的閘0 子任務前置檢查，見上方「分工」節。

## 狀態（2026-07-02）
- Tyrion Stop hook：已掛 settings.local.json 並**實戰攔截驗證**（引文誤攔為已知型態，待加引文白名單）。
- 三道閘 MVP：coach.py＋coach_rules.json（R001 保護路徑、R002 證據禁空話）＋Verifier subagent 已建。
- 跨工具：Codex/Antigravity 無原生 hook → 規則進 CODEX.md/GEMINI.md 開場必載＋輸出前自跑 reply_lint；**待 Claude 端驗穩後推全域**。
- 下一步：PreToolUse 契約閘（無契約擋 Write/Edit，opt-in）、跨 AI coach 接線、nightly 聚合高頻違規。
