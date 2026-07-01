# TaskLog — AI 助理框架 / 視覺品質試做 / 待辦整合
> 2026-07-02｜Claude@comaMacBookAir（AI 助理模式：Claude lead＋窗口，Codex/Antigravity 執行層）

## 🔴 下次重啟第一件事（最優先）
**確認 ody Stop hook 有執行**（hook 需重啟才生效，本對話已掛但未載）。驗法：故意寫含禁詞（如「好的/讓我來」）的收尾 → 應被 `tools/ody/squad/stop_hook.py` 擋下要求重寫。擋得住且無誤傷 → 回報使用者「這關穩了」→ 推全域（Claude `~/.claude/settings.json`＋規則進 CODEX.md/GEMINI.md/GLOBAL.md＋reply_lint 隨 sync 部署三工具）。

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

## 關鍵檔
- 框架：`tools/ody/`（README 有用法）；ody 小隊：`tools/ody/squad/`
- 討論/計畫：`_context/AI_TEAM_DISCUSSION_2026-06-24_*`、`_context/Plan_2026-07-01_discipline-harness.md`
- 交付：`outputs/AI助理框架_方案與實作_2026-06-24.html`、`outputs/assembly-guide-trial/`
