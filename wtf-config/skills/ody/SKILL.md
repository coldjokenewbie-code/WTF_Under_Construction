---
name: ody
description: 召喚奧德賽小隊（ody）——對當前任務套用三道閘紀律：動工前立契約、宣稱完成前機檢驗收＋獨立複驗、錯誤轉可機檢規則。任何專案可用。用法：/ody <任務描述>（新任務立約）、/ody check <task_id>（驗收）、/ody learn <糾正內容>（轉規則）。
---

# ody 奧德賽小隊

> 精神：Odysseus（多謀善變、從經驗學）＋Tyrion（守分寸、不信自律信守門）。
> 詳規：`<WTF_ROOT>/tools/ody/squad/ODY_SQUAD.md`。

## 錨點（先做）
讀 `~/.claude/wtf-root.txt` 得 `<WTF_ROOT>`；coach＝`<WTF_ROOT>/tools/ody/squad/coach.py`。
以下 `<PY>`：Mac/Linux=`python3`、Windows=`python`（看環境 Platform）。

## 角色
| 角色 | 職責 |
|---|---|
| Odysseus（策略/執行） | 拆任務、判風險、動工前立契約、增量實作 |
| Tyrion（輸出守門） | 回覆 lint：Claude Code 由 Stop hook 自動；其他工具輸出前自跑 `reply_lint.py` |
| Verifier（驗收） | 獨立複驗，禁自驗自過 |
| Mentor（學習） | 糾正/FAIL → 一條可機檢規則 |

## 三道閘流程

**閘1 立契約（無契約不動工）**：
```bash
<PY> "<WTF_ROOT>/tools/ody/squad/coach.py" new <專案>-<主題>-<YYYYMMDD> \
  --goal "..." --scope "受動路徑glob" --accept "驗收標準(逐條)" \
  [--verify-cmd "測試命令"] [--permission "授權點"] [--po-authorized]
```
- 在目標專案 cwd 下執行（契約自動綁該 repo；或 `--repo` 指定）。
- 授權點開頭一次向 PO 講定，過程不中途要權限。
- 動保護路徑（全域設定/settings）需 PO 明授＋`--po-authorized`。

**執行中**：每完成一條驗收標準即填證據（cmd 優先、會真跑記 exit；note 須具體，空話「已確認」會被擋）：
```bash
<PY> "<WTF_ROOT>/tools/ody/squad/coach.py" evidence <task_id> <編號> --cmd "驗證命令"
```

**閘2 驗收（宣稱完成前必 PASS）**：
```bash
<PY> "<WTF_ROOT>/tools/ody/squad/coach.py" check <task_id>
```
- FAIL → 修 → 重驗；禁跳過、禁只口頭說改好了。
- 獨立複驗（禁自驗自過）：Claude Code 派 `ody-verifier` subagent；其他工具換另一 AI headless 複驗（`claude -p`／`codex exec`／`agy --print`）。

**閘3 學習（犯錯即停工，先加規則才續）**：
- 工作違規/FAIL 重複同型 → `coach.py add-rule --rule-id R0xx --type banned_path_in_diff|evidence_note_not_generic|require_cmd_pass --msg "..."`。
- 回覆風格被糾正 → 樣式加進 `<WTF_ROOT>/tools/ody/squad/lint_rules.json` banned_phrases。
- 學習＝加可機檢規則，不寫心得；無法機檢者降 checklist 由 Verifier 人工核。

## 分工（可選，多執行者協作）

任務可拆給多個獨立執行者（Claude subagent／Codex headless／Antigravity headless／人工）各自領一份子契約做時用；單人單契約就夠的任務不必用這段。

**立子契約（同時掛回父契約）**：
```bash
<PY> "<WTF_ROOT>/tools/ody/squad/coach.py" assign <父task_id> <子task_id> \
  --agent codex --goal "..." --scope "受動路徑glob" --accept "驗收標準(逐條)" \
  [--verify-cmd "..."] [--permission "..."] [--repo ...]
```
- 子契約走一樣的三道閘（立約→填證據→check），跟一般契約無異；`--agent` 為 `claude`/`codex`/`agy` 時會印出對應 headless 派工指令範本（直接複製執行——同機優先直驅，跨機/GUI 才退回 `AGENT_SIGNAL.log`，同 ai-team 慣例）。
- 子契約 scope 應落在父契約 scope 之內：父契約自己的閘2a（scope 越界檢查）本來就會涵蓋子任務動到的檔案，不必另外驗證子集。

**父任務 check 前置閘**：`coach.py check <父task_id>` 會先查所有子任務是否已 `check` PASS，任一子任務缺契約或未過都直接 FAIL（訊息點名哪個子任務）——把 ai-team「輪流驗收、禁自驗自過」的精神改成機檢硬擋，不是流程約定。

**查子任務現況**（唯讀）：
```bash
<PY> "<WTF_ROOT>/tools/ody/squad/coach.py" children <父task_id>
```

## 回覆紀律（隨時）
結論先行、極簡、禁聊天語氣/浮誇/功勞詞；自評：`echo "草稿" | <PY> "<WTF_ROOT>/tools/ody/squad/reply_lint.py"`。
