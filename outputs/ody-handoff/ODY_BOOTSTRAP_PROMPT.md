# ody 小隊啟動 Prompt（貼進 Claude Code 即可開工）
> 用法：把 `ODY_PRD.md` 放進你的專案（建議 `_context/` 或專案根目錄），然後把下方分隔線內的內容整段貼給 Claude Code。

---

你現在是「奧德賽小隊（ody）」籌備負責人，擔任 Tech Lead。先完整閱讀專案內的 `ODY_PRD.md`（找不到就先問我路徑），依 PRD 建立 Phase 1 小隊。我是 PO。

## 執行步驟

**Step 0｜環境研究（先做，不准跳）**
研究你當前環境的 harness 能力並回報對照表：
- 有哪些 hook 事件可用（至少確認 Stop、PreToolUse、UserPromptSubmit）？settings 分幾層（user／project／local）？
- subagent 怎麼定義（`~/.claude/agents/` 或專案 `.claude/agents/`）？是否獨立 context？
- skills／slash command 怎麼註冊？
- hooks、agents、skills 各自熱載還是要新 session？（PRD §7-1 有原型答案，但以你實測為準）
不確定的用官方文件或實驗驗證，不准猜。

**Step 1｜前置授權（一次談定，中途不得追加）**
列出所有需要我授權的項目再開工，至少包含：
- 要改哪一層 settings 掛 Stop hook（建議先掛專案層，驗穩再升 user 層）
- 腳本與規則庫放哪個目錄
- 有無任何要花錢或對外連網的步驟（預設：無，全離線零依賴）

**Step 2｜實作 Phase 1 交付物（PRD §6）**
1. `reply_lint.py`＋`lint_rules.json`＋`stop_hook.py`（Tyrion）——鐵則：fail-open（腳本掛掉要放行）、防迴圈（檢查 `stop_hook_active`）
2. `coach.py` 契約檢查器，四個子命令：
   - `new`：立契約（task_id、goal、scope 白名單、驗收條款、驗證命令、授權點）
   - `evidence`：填證據（真跑命令記 exit code 與輸出尾段；禁「已確認」式空話）
   - `check`：機檢（scope 越界用 `git diff --name-only` 比白名單、逐條驗收證據、規則庫全套用）
   - `add-rule`：把 FAIL 轉成規則（起手支援三型：banned_path_in_diff／evidence_note_not_generic／require_cmd_pass）
3. Verifier subagent 定義檔：給它 task_id，它讀契約、重跑至少一條驗證命令、逐條判證據是否支撐驗收、回報 PASS/FAIL＋理由，≤60 行，只驗收不修改
4. 規則庫初始 2 條：R001 保護路徑需 PO 明授、R002 證據禁空話
5. 自測腳本：離線零依賴，至少覆蓋——scope 比對（含 `/**` 前綴）、R001 擋與放、R002 擋與放、git 解析回歸（quotepath＋porcelain 前導空白，見 PRD §7-3）

**Step 3｜dogfood 驗收（DoD）**
用「建置 ody 這件事本身」當第一個真任務：立契約 → 執行 → `check` → 有 FAIL 就修到 PASS → 派 Verifier subagent 獨立複驗。過程中你若違反任何一道閘（例如先動工後立約），**誠實記錄在報告裡**，並用 `add-rule` 或列入 Phase 3 待辦作為對策。

**Step 4｜交付報告**
給我一份研究報告（markdown 或 html），含：環境能力對照表、落地件清單與路徑、dogfood 過程（FAIL 了什麼、怎麼修）、規則庫現況、Phase 2/3 路線圖。**交付前不准 commit**，我驗收後才 commit。

## 工作紀律（全程有效）
- 結論先行、極簡回覆；FAIL 就說 FAIL 帶原始輸出，不美化
- 不動 scope 白名單以外的檔案；全域設定非我明授不碰
- 學習＝加一條可機檢規則，不是寫反省文
- 遇到 PRD 沒定義的決策：小事自己決並記錄，大事（花錢、動全域、改既有檔案）停下問我

---

## 附：Phase 2 預告（同事裝了第二個 AI CLI 後再貼）
> 屆時再給 Claude 這段：「ody 進 Phase 2：偵測本機可用的其他 AI headless CLI（如 `codex exec`、`gemini --print`），把 coach 驗收接上跨模型複驗（--peer 參數）；注意 headless 每次呼叫無狀態，多輪互動由你每輪重餵脈絡。先提方案與授權清單，不要直接改。」
