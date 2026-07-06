# Mission Loop：雲端自主任務迴圈（ody 小隊·自主執行層）
> 定案 2026-07-03（與使用者逐點討論拍板）。四層正名：對話優化=GLOBAL/playbooks；品質把關=三道閘（通用）；協作=ai-team；**自主執行=本檔**
> 讀者：被排程 trigger 喚醒的 fresh session（多為 Sonnet 級）。照規格逐步執行，不即興
> 時區鐵律：**cron 欄位是 UTC**（實證：nightly `0 19` 實際 19:08Z）；本檔所有人類時間=Asia/Taipei。棒內判斷時間一律 `TZ=Asia/Taipei date`

## 0. 定案參數

| 項 | 值 |
|---|---|
| 提醒棒 | 每日 17:00 台北（cron `0 9 * * *` UTC）：整理佇列現況＋今晚計畫，推播提醒使用者分派/核准 |
| 循環棒 | 每日 19:30/21:30/23:30/01:30 台北（cron `30 11,13,15,17 * * *` UTC；刻意避開 nightly `0 19` UTC 的同刻對撞），每棒 ≤2 小時 |
| 宵禁 | 台北 05:00 前收工（末棒 01:30 起跑＋≤2h 自然達成）；棒內見台北時間 ≥04:30 不開新增量 |
| 額度 | 不設數字上限（訂閱制打頂自然停）；白天 10:00–19:00 額度全留使用者 |
| 佇列 | 單鏈序列制：一次只推進一個 mission 的一個增量 |
| 停止閘 | 同一 mission 連續 2 棒零進展 → 標 `parked`＋通知；品味/不可逆決策 → 進 blockers 不阻塞 |
| 升級路徑 | one-shot 自續鏈（棒內自建下一顆 run_once trigger）＝v2，待第 4 節能力探測連續 3 晚 PASS 才啟用 |

## 1. 檔案結構（狀態＝repo，session 是無狀態的棒）

```
missions/
  QUEUE.md                 ← 佇列總表（使用者與 AI 共同編輯的唯一入口）
  <YYYYMMDD>-<slug>/
    MISSION.md             ← 方向、模糊標準錨點、硬底線、milestone（規劃棒產出，使用者核准）
    backlog.md             ← 增量清單（checkbox；執行棒逐項消化並更新）
    journal.md             ← 每棒一條 append-only：日期時間｜棒型（合法值僅：規劃棒/執行棒/定錨棒）｜做了什麼｜進展(yes/no)｜證據
    _blockers.md           ← 卡點停車場：需使用者決策/需本機/需外部 的事項，一事一條
```

**QUEUE.md 行格式**：`| <slug> | <狀態> | <優先序1-9> | <一句話方向> |`
狀態機：`待規劃 → 待核准 → active → done`；旁路：`parked`（零進展/被擋）。使用者把 `待核准` 改成 `active` ＝核准；改優先序＝調度。
**狀態比對鐵律：狀態欄必須與五個合法值「整欄精確相等」才算數；禁止子字串/grep 式匹配**（含括號註記的欄位一律視為不可作）。

**MISSION.md 必含段**（規劃棒照此產）：
```
# MISSION：<slug>
## 方向（一句話）
## 模糊標準錨點（2-3 個正例＋反例：什麼樣算好/算壞）
## 硬底線（可機檢的最低要求，逐條）
## Milestone（每個=一次使用者簽核點）
## 邊界（禁改清單／不做什麼／僅限 repo 內可完成）
```

## 2. 循環棒總規格（每次 cron 醒來照跑）

0. `cd` 到 WTF repo → `git pull`。讀本檔＋`missions/QUEUE.md`。
1. **秒退檢查**（任一命中即回報一行並結束，不做工）：
   - `TZ=Asia/Taipei date +%H%M` ≥ 0430；或 QUEUE 無 `待規劃`/`active` 項。
2. 取優先序最高的可作項，按狀態分派棒型：
   - `待規劃` → **規劃棒**（第 3.1 節）
   - `active` → 查該 mission `journal.md`：距上次定錨棒已 ≥5 個執行棒（journal 尚無定錨棒紀錄時，從該 mission 第一筆執行棒起算）→ **定錨棒**（3.3）；否則 → **執行棒**（3.2）
   - 其餘狀態跳過，看下一項。
3. 棒尾（每棒必做）：journal append 一條（含進展 yes/no＋證據）→ 觸發停止閘就改 QUEUE 狀態 → **只 add 本次動到的檔**（禁 `git add -A`）→ commit → `git pull --rebase`（rebase 衝突：`git rebase --abort`，journal 記「需人工」，不硬推）→ push main；**push 被拒（non-fast-forward）→ 再 `git pull --rebase` 後重推，最多重試 2 次**，仍失敗記「需人工」。
4. **派工紀律照舊制度**：粗活派 subagent 顯式帶 model（`playbooks/model-dispatch.md`）；產出過品質閘（fresh-context 驗收，交辦用 delegation-templates T5）；判斷疑難查 `judgment-rubrics.md`。

## 3. 三種棒型

### 3.1 規劃棒（mission 的第一棒，品質規格最高）
1. 讀 QUEUE 該行的一句話方向；掃 repo 相關現況（派 Explore 收結論）。
2. **多方案**：派 2–3 個 subagent（`model: opus`）各自獨立產分解方案（milestone＋前 5 個增量＋風險）。
3. **評審擇優**：再派一個 fresh-context subagent（`model: opus`）比較擇優並融合。
4. 產出 `MISSION.md`＋`backlog.md` 初版 → QUEUE 狀態改 `待核准` → 結束（**不開始執行**；使用者核准是開局唯一決策點）。

### 3.2 執行棒（標準增量）
1. 讀 MISSION.md（每棒都重讀，這是防漂移的錨）＋backlog 取最上面未勾項。
2. 增量尺寸：一棒內可完成＋可驗證；太大就先拆再做拆出的第一小項。
3. 做 → 交付物過品質閘（fresh-context read-back/測試，見 model-dispatch 第 6 節）→ 勾掉 backlog 項。
4. 撞到「需使用者決策／需本機資源／需外部資料」→ 寫入 `_blockers.md` 一條（含建議選項），**跳過換下一項**，不停等、不空轉。
5. 到 milestone → 是 MISSION **最後一個** milestone 且 backlog 全勾 → QUEUE 改 `done`；否則改 `待核准`（milestone 簽核後使用者再改回 active 續跑）。兩者都要：journal 記證據清單（讓使用者 3 分鐘能判）。

### 3.3 定錨棒（每 5 個執行棒插一根，防慢性漂移）
不做新增量。fresh-context 對照「近 5 棒 journal＋產出」vs「MISSION 方向句＋錨點」：
- 對齊 → journal 記「定錨 PASS」，順手整理 backlog 優先序。
- 小偏 → 修 backlog（記錄修了什麼、為何）。
- 大偏（產出方向與 MISSION 矛盾）→ mission 標 `parked`＋通知使用者，附偏航證據。
- 若累積了「模糊標準該修」的觀察 → 寫成提案進 `_blockers.md`（標準演化不自改 MISSION）。

## 4. v2 能力探測（one-shot 自續鏈升級判準）
每晚第一棒順手做一次（≤1 分鐘）：嘗試列出排程工具（如 `list_triggers`/`send_later` 是否可用），結果記入 journal（`chain-capability: PASS/FAIL`）。連續 3 晚 PASS → 在 `_context/nightly-notify.md` 提案升級 one-shot 自續鏈（30 分–2h 彈性棒距、先排後做自癒式），使用者核准後才改本檔與 trigger。

## 4.5 選題棒（本機 CLI，手動觸發，`/night-pick` skill）
本機才有全視野（各專案 TaskLog、Drive 專案），故選題在本機做、執行在雲端做。下班前使用者觸發一次：
1. 掃 `projects-registry.md` 本機專案清單，各讀 INDEX＋當前 TaskLog（三檔制，不全掃）收集候選工作。
2. **掛載過濾（硬條件）**：候選所屬 repo 必須在第 6 節「雲端掛載清單」內，否則剔除或標「僅限本機」。
3. **提名判準（四條全中才提名）**：影響大（解掉讓後續變快）／無阻塞（不等使用者決策即可動）／可增量（切得成 ≤2h 的塊）／低品味（驗收可機檢）。
4. 提名 2–3 個附理由 → **使用者核准後**才寫入 `missions/QUEUE.md`（狀態=`待規劃`）→ commit push main（只 add QUEUE.md，push 被拒照第 2 節重試規則）。選題官只提名不代決。

## 5. 提醒棒規格（17:00，獨立 trigger）
1. `git pull` → 讀 QUEUE＋各 active mission 的 `_blockers.md` 與最新 journal。
2. 產出 ≤15 行摘要：待核准清單／blockers 待決清單／今晚預計推進項／昨晚成果一句話。
3. 摘要寫入 `missions/QUEUE.md` 頂部「今日快報」段（覆蓋舊快報）＋commit push；結束時讓完成通知（推播）帶出摘要重點。
4. 佇列全空 → 摘要就一句：「佇列無任務，今晚循環棒將秒退；要派工請在 QUEUE.md 加一行」。

## 6. 邊界與誠實條款
- 雲端棒只及**已掛載 repo**。掛載清單（2026-07-03 查證自 nightly trigger 環境，之後以 claude.ai/code → Routines → Repositories 為準，增刪後回寫本行）：WTF_Under_Construction、Assembly_Plant_Mobile_Guide、Planner2Line、Remotion_fun、claude_CDIC_O4、Aseembly_Plant_Interactive_machine、HsinchuScienceEducationCenter、cowork_CDIC、attendance-dashboard、S-reclaimed-water-plant、SouthLibrary、ppt_map_mark。
- 需本機/實機的工作一律進 blockers，不假裝能做。
- 「5 小時額度窗」與週上限的精確行為未確認；夜鏈集體沉默時先懷疑打頂，提醒棒隔天會從 journal 斷點看出並回報。
- 本檔屬黃區（maintenance-protocol）：棒子只能照做，改規格走提案。
