# TaskLog 2026-07-03：Fable 5 制度建置
> session：Claude Code web（remote），模型 claude-fable-5（唯一一次）。分支 `claude/fable5-system-design-rp1t6i`
> 目標：把高階判斷轉成弱模型可長期沿用的制度檔，不執行日常任務

## 完成項目

1. **A 快速診斷**：`wtf-config/playbooks/harness-diagnosis.md`——最漏 token（開場全量載入）、最易失焦（主對話下場做粗活）、最易出錯（自驗自過）三名各附修法與判準。
2. **B 常載鏈重寫**（舊版備份 `wtf-config/archive/2026-07-03_pre-fable5/`）：
   - GLOBAL.md 208→116 行：新增「制度層」（派工鐵律＋playbooks 路由表）；溝通細則收斂到 AGENTS.md（正本）；Multi-Agent 底線與 AI 衰退因應抽成 playbooks。
   - CLAUDE_CODE.md 81→38 行（入口索引化）；前端/office/worktree 踩坑抽成 `pitfalls-frontend.md`、`pitfalls-office-docs.md`、`parallel-worktree.md`。
   - 開場「讀取 `_context/` 所有 .md」矛盾指令 6 處（GLOBAL/CLAUDE_CODE/AGENTS/GEMINI/CODEX/CLAUDE_COWORK）統一為**三檔制**：INDEX → 當前 TaskLog → lessons-learned。
   - 常載鏈合計 241 行（上限 500）；專案 `.claude/CLAUDE.md` 改為索引。
3. **C 模型調度守則**：`playbooks/model-dispatch.md`——派工門檻、交辦三要素、回報合約、model 調度表（2026-07-03 查證值）、升降級路徑、驗證不自驗。
4. **D 判斷力外化**：`playbooks/judgment-rubrics.md`——R1 升級／R2 完成／R3 停問／R4 換路／R5 品質底線／R6 context 自管，每條正反例。
5. **E 交辦範本**：`playbooks/delegation-templates.md`——搜尋/實作/重構/研究/審查五式＋通用回報合約＋派工前自檢。
6. **F 維護協議**：`playbooks/maintenance-protocol.md`——綠黃紅分區、教訓回寫格式、觸發式精簡門檻。
7. **G 交接信**：`playbooks/letter-from-fable5.md`——三件要事、退化預防表、低信心產出誠實清單。
8. LESSONS.md 登錄一行；本 TaskLog。

## 未解決問題

- P1：制度落地非 Claude 工具（Antigravity/Codex）未實測，僅改文字（見信件低信心清單 #3）。
- P1：「被導向 Opus 4.8 的請求算誰的額度」查不到，待使用者到 usage 儀表板實測後回填 `model-dispatch.md` 第 0 節。
- P2：把三檔制/派工鐵律轉成 ody 機檢規則（信件「第 2 件事」），未動工。
- P2：本機（Mac/Win）跑 `sync_config.py sync` 後才會把新 CLAUDE_CODE.md 部署到 `~/.claude/CLAUDE.md`；remote 分支需先 merge main。

## 主要輸入檔案

- 舊常載鏈備份：`wtf-config/archive/2026-07-03_pre-fable5/`
- 既有制度參照：`_context/Plan_2026-07-01_discipline-harness.md`、`tools/ody/squad/ODY_SQUAD.md`

## 第二階段（同日晚間）：Mission Loop 定案與落地

與使用者逐點討論定案：四層正名（三道閘抽為通用品質層；ody 本體＝自主執行層）、雲端 cron 圍欄制自動串接（one-shot 自續鏈因「trigger 開出的 session 無排程 MCP 工具」降為 v2，見 mission-loop.md 第 4 節能力探測）、時段圍欄取代額度數字上限。
落地：`wtf-config/playbooks/mission-loop.md`（棒型規格/檔案結構/定案參數）＋`missions/QUEUE.md`＋兩顆 cron trigger——
- `trig_01QfiWWWqna4CoG9oU4juEUq` 提醒棒：`0 9 * * *` UTC＝台北 17:00，推播開。
- `trig_015YB7a5ne6YP9jrhNo6ejLk` 夜間循環棒：`30 11,13,15,17 * * *` UTC＝台北 19:30/21:30/23:30/01:30，推播關（日報由提醒棒統一推）。原 `0 ...,19` 末棒與 nightly `0 19` UTC 同刻對撞，審查抓到後改半點錯開＋棒尾 push 重試 2 次。
- **cron 一律 UTC**（實證自 nightly trigger next_run_at）。trigger 掛載 repo 清單沿用 nightly 的環境（12 repos）；registry 增刪後仍需回 Routines UI 補掛。

## 下一步建議

1. 使用者本機 merge 此分支 → 跑 `sync_config.py sync` → 開新 session 驗證開場只讀三檔。
2. 用 2-4 週後依實感調數字門檻（300 行/3 檔/兩輪重試），走黃區提案。
3. 挑一條文字規則轉 ody 機檢（建議先做「已完成需證據」）。
