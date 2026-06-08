# Nightly 排程 Prompt
> 此檔案為 claude.ai/code 排程 Trigger 的 prompt 來源，請直接複製內容貼入排程設定。
> **更新此檔後，需把內容貼回 claude.ai/code 的排程 trigger 才會生效。**

---

【Nightly 自動任務】

先 `cd` 到 WTF repo（雲端 clone 路徑，通常 `/home/user/WTF_Under_Construction`），回應「已開始 Nightly」後依序執行。

> 環境註記：本排程跑在雲端 ephemeral container。
> 1. **拿不到本機（Win/Mac）的工作 transcript** → 學習來源＝**各 repo 今日 git commit messages**（真實工作已 push 上 GitHub），不分析不存在的本機 session。
> 2. **雲端直連 github.com 無憑證、不能 `git clone`**。可掃的 repo＝**已在 trigger「Repositories」欄掛載、由環境預先 clone 到 `/home/user/<repo>` 的那些**。registry 增刪 repo 後，**必須回 trigger UI（claude.ai/code → Routines → 每日工作回顧 → Edit → Repositories）同步重掛**，否則掃不到。

---

## 1. Git Log 掃描（從 `projects-registry.md` 取清單，掃已掛載 repo）

**不硬編 repo 清單**——從 `wtf-config/projects-registry.md` 的 `github` 欄取。對每個 repo：已掛載者 pull＋掃今日 commit；未掛載者明確標出，不靜默漏掉。

```
export TZ='Asia/Taipei'                 # 用台灣時區定義「今日」，避免 UTC 切日漏抓晚間 commit
TODAY=$(date +%Y-%m-%d)
REG=/home/user/WTF_Under_Construction/wtf-config/projects-registry.md
# 解析表格：col1=project、col2=github；跳過表頭/分隔/未確認「（」開頭。dir=repo basename（git@ 與 https 皆適用）
grep '^|' "$REG" | sed 's/^| *//; s/ *| */|/g' \
 | awk -F'|' 'NR>2 && $2 ~ /github/ && $2 !~ /^（/ {print $1"\t"$2}' \
 | while IFS=$'\t' read -r project url; do
     dir=$(basename "$url" .git)
     echo "### $project ($dir)"
     if [ -d "/home/user/$dir/.git" ]; then
       git -C "/home/user/$dir" pull -q 2>/dev/null
       git -C "/home/user/$dir" log --since="$TODAY 00:00" --date=local \
         --format="%h %ad %s" 2>/dev/null || echo "  （今日無活動）"
     else
       echo "  （未掛載：trigger Repositories 未含此 repo，無法掃描 → 需回 trigger 補掛）"
     fi
   done
```

整理各 repo 今日提交清單（無提交標「今日無活動」；未掛載標「未掛載」並在最終回報提醒補掛）。

---

## 2. 從 commit 萃取 Lesson 候選

讀今日各 repo commit messages（尤其 `lesson-add` / `fix` / `refactor` / 踩坑修正類），判斷：
- 是否有**尚未寫入 SSOT** 的可重用教訓（跨工具原則／Claude Code 操作／特定專案邏輯）。
- **多數 lesson 在本機工作時已 lesson-add**；只補「commit 顯示有 take-away 但 SSOT 還沒記」的淨新項，避免重複。

層級：跨工具原則→`全域`(GLOBAL.md)；Claude Code 操作→`工具 code`(CLAUDE_CODE.md)；專案邏輯→`專案`(該 repo `_context/lessons-learned.md`)。

---

## 3. 寫入 lesson（加性）+ 雲端索引

對每條淨新 lesson：
- 工作層：寫入對應 `_context/lessons-learned.md`（整合進既有段落、去重精簡，不新增冗段）。
- 雲端層：同步登一行到 `wtf-config/LESSONS.md`（`專案｜日期｜一句話｜連結`）。

---

## 4. 寫入 Session Log

建立 `session-logs/YYYYMMDD.md`：

```markdown
# YYYY-MM-DD Session Log（Nightly 自動產出）

<全域變更通知區塊，見第 6 步——放最上方>

## 今日 Git 活動
- [repo]：[提交摘要]（未掛載者另列，提醒補掛）

## 自動歸檔 Lessons
- [層級] [內容]（或「本次無淨新 lesson」）
```

---

## 5. 全域設定（GLOBAL.md / wtf-config SSOT）—— 只「建議」，**不可自行修改**

可檢視 `wtf-config/GLOBAL.md` 及其他 SSOT 設定檔，找出矛盾／重複／過時／冗長之處，但 **routine 一律只「提出建議」，不得直接編輯這些檔**（全域設定的改動權保留給用戶）。把建議寫進第 6 步的 NOTIFY 檔，由用戶核准後才套用。

> 範圍界定：
> - **可自動改（加性知識）**：`_context/lessons-learned.md`、`wtf-config/LESSONS.md`（新增 lesson、整合去重）、`session-logs/`、`_context/nightly-notify.md`。
> - **只能建議、禁自改（全域設定）**：`wtf-config/GLOBAL.md`、`CLAUDE_CODE.md`、`CODEX.md`、`GEMINI.md`、`AGENTS.md`、`sync_config.py`、`projects-registry.md` 等。
> - **不碰**：`dashboard.html`／`outputs/dashboard.html`（本機 `sync_config.py dashboard` 產）。

---

## 6. 全域設定「修改建議」→ 寫 NOTIFY 檔

若本步有任何「**建議修改全域設定**」，**append** 到 `_context/nightly-notify.md`（不存在則建立）：

```markdown
- [ ] YYYY-MM-DD nightly 建議修改全域設定（待用戶核准）
  - <檔名>：<建議內容＋理由，一行>
```

- 此檔 commit 進 main → 用戶本機 hook pull → **下次 session-start 開場浮出**（見 session-start skill）。用戶核准後自行套用並清除該行；不核准就刪該行。
- 最終回報開頭：有建議→`## 💡 本次有 N 項全域設定修改建議（已寫入 nightly-notify.md，待你核准）`＋列出；無→`✅ 本次無全域設定修改建議`。
- 若第 1 步有 repo 標「未掛載」，於回報附一句：`⚠️ 下列 repo 未掛載 trigger、本次未掃：…，請回 trigger Repositories 補掛`。
- **強調：routine 從不直接改全域設定檔，只寫建議。**

---

## 7. Commit & Push（只推**加性**內容進 main）

```
export TZ='Asia/Taipei'
YYYYMMDD=$(date +%Y%m%d)
cd /home/user/WTF_Under_Construction
git pull --rebase origin main || { echo "rebase 衝突，abort 不硬推，回報需人工處理"; git rebase --abort; exit 0; }
git add session-logs/ _context/lessons-learned.md wtf-config/LESSONS.md _context/nightly-notify.md
# 各 repo 專案層 lesson 同理只 add 該檔
git commit -m "nightly-$YYYYMMDD: [今日一句話摘要]"
git push origin main
```

- **只 `git add` 加性檔**（session-logs／lessons／LESSONS／nightly-notify），**不 `git add -A`**——確保全域設定檔即使被誤動也不會被提交。
- **commit 進 main**（取代舊版「push 到永不 merge 的 `claude/nightly-*` 分支」——那讓自動更新全卡死、不生效）。
- **衝突一律 abort 不硬推**，回報標「需人工」，不破壞 main。
- 各 repo 的專案層 lesson 若有改，於該 repo 同樣 `pull --rebase → commit → push origin main`，衝突即 abort。
