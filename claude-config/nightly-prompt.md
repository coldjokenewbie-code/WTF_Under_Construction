# Nightly 排程 Prompt
> 此檔案為 Remote Trigger 的 prompt 來源，請直接複製內容貼入排程設定。
> 更新此檔案後需同步更新 claude.ai/code 的排程 trigger 內容。

---

【Nightly 自動任務】

第一步，先執行：
bash /root/.claude/hooks/sync-claude-md.sh

載入完成後回應「已載入全域設定」，再依序執行以下工作。

---

## 1. Git Log 掃描

讀取 /home/user/WTF_Under_Construction/projects.md，對列出的 8 個 repo 執行今日提交掃描：

```
TODAY=$(date +%Y-%m-%d)
for repo in WTF_Under_Construction Planner2Line reader_syc Assembly_Plant_Mobile_Guide Agent_Skills claude_CDIC_C1 claude_CDIC_A1 CDIC_B1; do
  git -C /home/user/$repo log --oneline --since="$TODAY 00:00" --format="%h %ai %s" 2>/dev/null
done
```

整理各 repo 今日提交清單。

---

## 2. Session Transcript 分析

掃描今日（mtime 在當日）的 transcript 檔案：

```python
import json, os, glob, time
from datetime import datetime

transcript_dir = "/root/.claude/projects/-home-user"
today = datetime.now().strftime("%Y-%m-%d")
today_ts = datetime.strptime(today, "%Y-%m-%d").timestamp()

files = glob.glob(f"{transcript_dir}/*.jsonl")
today_files = [f for f in files if os.path.getmtime(f) >= today_ts]
```

對每個 transcript：
1. 解析 JSONL，只讀 `type=user` 和 `type=assistant` 的 message，過濾掉 tool_use / tool_result block
2. 判斷工作內容：專案（從 cwd 或對話判斷）、完成事項、遇到的錯誤或走錯的路、重要決策
3. 輸出 lesson 候選（每條一句話 + 建議層級）

**層級判斷原則**：
- 跨工具都適用的溝通、思考原則 → `全域`
- Claude Code 操作流程、git、檔案習慣 → `工具 code`
- 特定專案業務邏輯 → `專案`（對應 repo 的 `.claude/CLAUDE.md`）

---

## 3. 自動 Lesson-Add

對每個有效 lesson 候選執行寫入，使用 lesson-add skill 規範：
- 整合進既有段落，不新增段落
- 去重、去冗餘、精簡

每條 lesson 寫入後 commit（`lesson-add(層級): 摘要`）。

---

## 4. 寫入 Session Log

建立或 append `/home/user/WTF_Under_Construction/session-logs/YYYYMMDD.md`：

```markdown
# YYYY-MM-DD Session Log（Nightly 自動產出）

## 今日 Git 活動
- [repo]：[提交摘要]

## Session 分析
### Session [uuid 前8碼] — [專案/cwd]
- 工作內容：...
- 遇到的問題：...
- 決策：...

## 自動歸檔 Lessons
- [層級] [內容]
```

---

## 5. 更新儀表板

更新 `/home/user/WTF_Under_Construction/dashboard.html`：
- 討論記錄新增今日 Nightly 條目（git 摘要 + lesson 數量）
- 已完成的待辦項目標為 done

---

## 6. 清理知識庫

檢查 `claude-config/CLAUDE.md`：
- 互相矛盾 → 保留較新較具體的版本
- 重複 → 合併
- 過時 → 移除
- 每條規則能否一句話說清楚 → 精簡

---

## 7. Commit & Push

```
YYYYMMDD=$(date +%Y%m%d)
git -C /home/user/WTF_Under_Construction add -A
git -C /home/user/WTF_Under_Construction commit -m "nightly-$YYYYMMDD: [今日一句話摘要]"
git -C /home/user/WTF_Under_Construction push -u origin claude/nightly-$YYYYMMDD
```

不 merge 到 main。
