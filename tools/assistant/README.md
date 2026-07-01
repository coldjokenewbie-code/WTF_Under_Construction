# assistant — AI 中立的自主任務助理框架（方案 B MVP）

> 來源：ai-team 討論 `_context/AI_TEAM_DISCUSSION_2026-06-24_ai-assistant-framework.md`
> Tech Lead：Claude；執行/驗收：Codex、Antigravity（headless 三方）

## 它解決什麼
打造一個**不綁定特定 AI**、能**自主完成任務**、且**省 API、低風險、會自動學習**的助理框架。

四大支柱：
1. **本地優先（省 API）**：任務先查 registry，命中就跑確定性 handler，**完全不呼叫 LLM**；只有未本地化/失敗才 fallback 到 LLM。
2. **AI 中立**：`adapter.py` 把「呼叫 LLM」抽象成統一介面，底層 `claude / codex / agy` 可換；框架不綁任一家。
3. **低風險（Policy Gate 雙層）**：建構前 `check_command` + 執行前 `executor` 重檢；拒網路/破壞性/注入/路徑穿越，寫入限白名單目錄，禁 `shell=True`。
4. **自動學習（複利）**：每步寫結構化事件 → `learn.py` 算「省 API/複利」指標，偵測重複 fallback → 產**升級草案 `.draft`**（待 PO 審核，不自動生效）→ 升級成 handler 後該類任務 llm_calls→0。

## 目錄
```
tools/assistant/
  run_task.py          Orchestrator 進入點
  learn.py             學習：算指標 + 產升級草案
  core/
    spec/validate.py   零依賴 JSON Schema 驗證（不裝外部套件＝省）
    policy.py          Policy Gate（denylist + 白名單 + 反穿越）
    executor.py        受控 executor（只吃 argv list，永不 shell=True）
    registry.py        task_type → 確定性 handler（含 version + I/O 契約）
    adapter.py         AI 中立 adapter（dry-run 預設不花 API）
    events.py          結構化事件 → data/events.jsonl（schema 驗證）
    context.py         handler 的受控介面（run_cmd / write_output）
    paths.py           路徑錨點（禁裸相對路徑）
  handlers/            確定性處理器（project_digest, config_sync_check）
  schemas/             task_spec / event 的 JSON Schema（鎖定格式）
  tasks/               任務 spec 範例
  tests/test_safety.py 自驗套件（24 項，可離線跑）
```

## 用法
```bash
# 跑任務（本地確定性，零 LLM）
python3 tools/assistant/run_task.py tools/assistant/tasks/project-digest.task.json

# 自驗（離線、24 項）
python3 tools/assistant/tests/test_safety.py

# 學習：算指標 + 產升級草案
python3 tools/assistant/learn.py

# 看 registry 契約
python3 tools/assistant/run_task.py --dump-registry

# fallback 預設 dry（不花 API）；要真呼叫 LLM 才加 --allow-llm 且 spec.constraints.allow_llm=true
python3 tools/assistant/run_task.py <spec.json> --allow-llm --backend codex
```

## 新增一個確定性任務（讓它「學會」一類工作）
1. 在 `handlers/` 寫 `def run(spec, ctx) -> HandlerResult`，只透過 `ctx.run_cmd` / `ctx.write_output` 動作。
2. 在 `core/registry.py` 的 `REGISTRY` 註冊 `task_type → handler`（填 version + I/O 契約）。
3. 寫一個 `tasks/<name>.task.json`，跑 `run_task.py` 驗證。
> 通常由 `learn.py` 的升級草案觸發：某類任務重複 fallback → PO 審核草案 → 照上面 3 步本地化 → 下次 llm_calls=0。

## 與 WTF 既有機制的接點
- 學習產物對接兩層 lessons（`_context/lessons-learned.md` / `wtf-config/LESSONS.md`）。
- 升級草案的 PO 審核流程同 `nightly-notify.md`（draft → 人工核准才生效）。
- `config_sync_check` handler 直接複用 `wtf-config/sync_config.py check`。

## 三個建置層級方案（PO 可選）
- **方案 A 就地擴充 WTF**：用既有 hook/skill/lessons/nightly 延伸，最省、半自動。
- **方案 B 獨立本地 Orchestrator（本 MVP，推薦）**：本檔即是。中立/自主/省 API/可學習皆到位，可分階段。
- **方案 C 全自動事件驅動 daemon**：B + 常駐 daemon + 任務佇列 + 跨機派工 + 複利 dashboard。最自主、成本最高。
