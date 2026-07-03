# 制度檔維護協議
> 適用：任何 AI 要改 `wtf-config/` 或制度相關檔案之前，先讀本檔
> 原則：制度是可累積資產。改之前先分區——綠區直接改，黃區先提案，紅區不碰

## 1. 分區表（改檔前查這裡）

### 綠區——可自行改，改完在回報中列出即可
| 檔案 | 允許的改法 |
|---|---|
| 各專案 `_context/` 的 TaskLog、Handover、INDEX、lessons-learned | 照命名慣例新增/更新；結案歸檔 |
| `workingfiles/`、`outputs/` | 依 GLOBAL.md 檔案規範自由使用 |
| `wtf-config/LESSONS.md` | **只加行**（`專案｜日期｜一句話｜連結`），不改不刪既有行 |
| `playbooks/model-dispatch.md` 第 0 節型號表 | 查證到新值即更新，**必附查證日期與來源**（claude-code-guide／官方文件） |
| `playbooks/pitfalls-*.md` | **只追加**新踩坑條目（格式見第 2 節），不改不刪既有條目 |

### 黃區——先提案、使用者核准後才改
| 檔案 | 原因 |
|---|---|
| 常載鏈：`GLOBAL.md`、`CLAUDE_CODE.md`、`AGENTS.md`、`GEMINI.md`、`CODEX.md`、`CLAUDE_COWORK.md`、`CLAUDE_CHAT.md` | 每個 session 都吃，改壞影響全部工作（沿用 nightly「只建議不自改」慣例） |
| playbooks 的規則本文（dispatch 規則、rubric、範本、本檔） | 制度骨架，改壞會被弱模型放大執行 |
| `sync_config.py`、`projects-registry.md`、`machines.md` | 部署機制，改壞會斷跨機同步 |
| `skills/*/SKILL.md`、`agents/*.md` | 影響所有觸發該 skill 的 session |
| `settings.json`／hooks | 權限與自動化，安全敏感 |

**黃區提案格式**（二選一路徑：當面問使用者，或寫入 `_context/nightly-notify.md` 待核准）：
```
提案：改 ｛檔案｝
現文：｛原文引用，含行號｝
改為：｛新文｝
理由：｛觸發此提案的實際事件｝
影響：｛哪些 session/工具會吃到｝
```

### 紅區——不碰
- `wtf-config/archive/`（含 `2026-07-03_pre-fable5/` 備份）：歷史存證，只讀。
- `playbooks/letter-from-fable5.md`：原文保存。有回應或後續，另開新檔（如 `letter-response_YYYY-MM-DD.md`）。

## 2. 踩雷教訓寫回哪裡（格式固定）

1. **當下**：寫進該專案 `_context/lessons-learned.md`（工作層，詳述），格式：
   ```
   ### YYYY-MM-DD ｛主題｝
   - 坑：｛發生什麼、怎麼發現｝
   - 修：｛怎麼解的，含命令/程式片段｝
   - 防：｛下次怎麼避免，一句可執行的話｝
   ```
2. **同一次工作內**：到 `wtf-config/LESSONS.md` 加一行索引（綠區）。
3. **屬於特定主題的技術坑**（前端/office/並行）：追加到對應 `playbooks/pitfalls-*.md`（綠區，只追加）。
4. **屬於制度執行的坑**（派工錯、驗證漏、判斷失誤）：評估是否該改 rubric/dispatch 規則 → 走黃區提案，不直接改。

## 3. 累積多長要精簡（觸發式門檻，session-end 時順檢一項）

| 對象 | 門檻 | 動作 |
|---|---|---|
| 常載鏈合計（`cat GLOBAL.md CLAUDE_CODE.md AGENTS.md \| wc -l`） | >500 行 | 黃區提案：抽內容到 playbooks |
| 入口檔（CLAUDE_CODE.md 或任一工具入口） | >150 行 | 黃區提案：索引化 |
| 各專案 `lessons-learned.md` | >200 行 | 舊條目移 `_context/archive/lessons-YYYY.md`，留最近 6 個月 |
| 單一 playbook | >200 行 | 拆分或去重（黃區提案） |
| `LESSONS.md` 索引 | >150 行 | 按年拆檔（黃區提案） |
| INDEX.md「現況」段 | >15 行 | 直接壓縮成一段（綠區，INDEX 本來就該短） |

## 4. 誰來執行維護

- **每次 session-end**：檢查第 2 節該寫的教訓寫了沒；順檢第 3 節門檻**一項**（輪流，不必全查）。
- **nightly routine**：聚合各專案新 lessons 到 LESSONS.md；常載鏈改動一律只產提案（沿用既有 nightly-notify 流程）。
- **使用者**：黃區核准；每月看一次 `playbooks/harness-diagnosis.md` 的判準有沒有再犯。
