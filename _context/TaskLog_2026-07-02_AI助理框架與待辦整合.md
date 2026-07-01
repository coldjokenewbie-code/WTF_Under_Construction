# TaskLog — AI 助理框架 / 視覺品質試做 / 待辦整合
> 2026-07-02｜Claude@comaMacBookAir（AI 助理模式：Claude lead＋窗口，Codex/Antigravity 執行層）

## 🔴 下次重啟第一件事（最優先）
1. **全域 Stop hook 生效驗證**（已升 `~/.claude/settings.json`，hook 不熱載）：任意專案新 session 驗禁詞被攔。
2. **ody-verifier 首次實跑**：派 subagent 獨立複驗契約 `ody-global-20260702`（禁自驗自過首戰）。※agent 定義實測**熱載**（部署即列清單），不必等新 session。
3. Stop hook 誤攔改良：引文/測試脈絡白名單。4. PreToolUse 契約閘（無契約擋 Write/Edit，opt-in）。

> ✅（2026-07-02 完成）「確認 Stop hook 有執行」：實戰攔截驗證通過（block+強制重寫）。Tyrion 全域化已完成（見 §6）。

## 本次完成

### 1. AI 中立自主任務助理框架 MVP（方案 B）
- `tools/assistant/`（889 行 Python，零外部依賴）：Orchestrator + Policy Gate 雙層 + 受控 executor(禁 shell=True) + registry(版本+I/O契約) + AI 中立 adapter(claude/codex/agy，dry 預設不花 API) + 結構化事件 log(schema 驗證) + learn(複利指標+升級草案) + 前置授權評估(5 類授權點硬規則) + handlers(project_digest / config_sync_check / kiosk_build_verify)。
- 自驗 30/30；3 輪討論＋1 輪輪流驗收(Codex PASS、Antigravity 抓 3 安全洞→修+回歸→CLOSED-PASS)。
- 討論全程：`_context/AI_TEAM_DISCUSSION_2026-06-24_ai-assistant-framework.md`；交付 `outputs/AI助理框架_方案與實作_2026-06-24.html`。
- 紀律 harness 設計（教練/品管制）：`_context/Plan_2026-07-01_discipline-harness.md`（待實作）。

### 2. 視覺品質試做（組立工場導覽 App 首頁）
- `kiosk_build_verify` handler：headless 截圖＋逐項機檢（斷圖/console/溢出/字數），零 LLM。
- 3 版初稿(emoji/CSS 幾何) 被 PO 打回：純視覺對標得獎博物館 App 僅 1-2 分（不及格）。
- 迭代到「真實 PD 史料照＋極簡＋大留白」路線；輪流當 lead 各 1 版（`outputs/assembly-guide-trial/`：v4_史料滿版=Claude、lead_codex_儀表檔案、lead_agy_電影硬切）。PO 排序 1>3>2。
- 史料照：Baldwin Locomotive Works 組立工場 c.1905，NYPL Dennis 收藏，公共領域，已標來源。

### 3. 待辦整合（語音 → TaskLog + 待辦 App）✅ 已上線
- 定案：**TaskLog=待辦真相源；待辦 App(ai-team-todo)=跨專案鏡像總覽(owner 分 我執行=user/AI 執行=AI)；廢 INBOX.md**。
- 改 `/inbox` skill + GLOBAL「待辦系統」段，已 sync 部署三工具、commit+push（`5f84d24`）。
- 實測一筆「工作 組立英國俘虜」走完全程：Assembly TaskLog 加「📥 語音待辦」＋App 新增 `[·] 組立/導覽｜組立英國俘虜｜(AI@…)`＋原檔移 Ingested＋Assembly commit push(`a9dd9b1`)。
- 修坑：skill 收尾 `git add _context/` 太寬 → 收窄成只 add 本次 TaskLog 檔。

## 未解決 / 下一步
- 視覺：PO 要 8+（目標超越得獎 11）；史料滿版(第一名)待再精修，8→11 需更強素材/工藝，PO 授權可抓免費圖/生成。
- 紀律 harness（教練/品管制）：設計完成，待實作（契約檢查器 + coach.py + rules/coach-rules.md）。
- 待辦：剩「工作 say something.md」未處理（空內文、疑個人/測試）。
- assistant 框架：PO 未拍板採 A/B/C 哪案續推；kiosk 視覺自驗的「驗不過→LLM 修→再驗」整圈未接。

## 4. 奧德賽小隊（ody）籌備（本次後半）
- 框架改名 `tools/assistant/` → `tools/ody/`（30/30 無損）。
- 根因定案：規範停 prompt 層、無輸出檢查＝靠自律必漂移；解＝輸出守門 lint + 錯誤轉可機檢規則（複利）。
- 編組：Odysseus(策略/執行)、Tyrion(守門)、Mentor(學習)、Verifier(驗收)。
- 已建測：`tools/ody/squad/`＝`reply_lint.py`(禁詞+字數)、`lint_rules.json`(規則庫)、`stop_hook.py`(Stop hook，block/放行/防迴圈/fail-open 皆驗)、`ODY_SQUAD.md`。
- Stop hook 已掛 `.claude/settings.local.json`（使用者授權）；**但 hook 需重啟才生效**（查證：官方無熱載）。
- 研究報告：`outputs/ody籌備_研究報告_2026-07-02.html`。
- 跨工具（Codex/Antigravity 無原生 hook）：規則寫進 CODEX.md/GEMINI.md 開場必載 + 輸出前自跑 reply_lint 自檢。**待 Claude 這關驗穩後推全域。**

## 5. ody 三道閘 MVP（2026-07-02 續，Plan_2026-07-01 待建清單落地）
- `tools/ody/squad/coach.py`：閘1 立契約(new)／執行中填證據(evidence，cmd 真跑記 exit)／閘2 機檢(check：scope 越界+證據逐條+handoff 行數+verify_cmds+規則全套用)／閘3 學習(add-rule)。事件入 events.jsonl（schema 增 4 個 coach phase）。
- `coach_rules.json`：R001 保護路徑需明授、R002 證據禁空話。`test_coach.py` 自測 8/8；safety 30/30 不退步。
- `.claude/agents/ody-verifier.md`：Verifier subagent（獨立 context 驗收，待新 session 生效）。
- dogfood：本任務自立契約 `ody-mvp-20260702` 走完 FAIL(6項)→修→PASS。**兩個真 bug 由自驗抓出**：porcelain 首行前導空白被 strip 吃掉致路徑掉首字；git 非 ASCII 檔名八進位跳脫致 scope 誤判（修=core.quotepath=false）。
- **誠實記錄：本任務違反閘1（先動工後立約）**——證明無機器強制點必漂移；根治＝PreToolUse 契約閘（下一步）。
- 報告：`outputs/ody初期編組與harness研究_2026-07-02.html`。

## 6. ody 全域化（2026-07-02 續）——任何專案可召小隊
- **入口**：`/ody` skill（SSOT `wtf-config/skills/ody/`）已 sync 部署三工具（~/.claude、~/.codex、~/.gemini 各 12 skills），本 session 即時可見。
- **Tyrion 全域**：Stop hook 升至 `~/.claude/settings.json`（user 層，PO 明授）；WTF 專案層重複 hook 已移除。**新 session 才生效**。
- **Verifier 全域**：SSOT 移 `wtf-config/agents/ody-verifier.md`，sync_config.py 新增 agents 部署＋check 段 → `~/.claude/agents/`；專案層副本已刪。
- **coach 多 repo**：契約記 `repo_root`（預設 cwd 所在 repo，`--repo` 可指定），git/驗證命令都對目標 repo 跑；於 scratchpad 臨時 repo 實測越界 FAIL→修→PASS（契約 `odytest-multirepo`）。契約/規則庫仍集中 WTF＝跨專案共用學習。
- 本任務契約 `ody-global-20260702` 全閘 PASS（coach 抓出 3 FAIL 修正後過：test_coach 對 git rm 檔的存在性誤判、evidence one-liner 筆誤）。
- **Windows 待辦已入 App**（f477bdb2）：pull+sync＋手動掛 Stop hook＋新 session 驗證。
- 🔴 新 session 驗證點：任意專案 (1) Stop hook 攔禁詞 (2) `/ody` 可召 (3) ody-verifier 出現在 agent 清單。

## 關鍵檔
- 框架：`tools/ody/`（README 有用法）；ody 小隊：`tools/ody/squad/`
- 討論/計畫：`_context/AI_TEAM_DISCUSSION_2026-06-24_*`、`_context/Plan_2026-07-01_discipline-harness.md`
- 交付：`outputs/AI助理框架_方案與實作_2026-06-24.html`、`outputs/assembly-guide-trial/`
