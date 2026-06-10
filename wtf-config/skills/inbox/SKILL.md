---
name: inbox
description: 分流語音速記 inbox。把 Obsidian vault Clippings 中「工作」開頭的速記，判定所屬專案後寫入該專案 _context/INBOX.md、commit/push，再把原檔移入 Ingested。手動觸發。
---

# Inbox 分流（WTF 控制面 Phase B）

把手機語音速記（Obsidian on Google Drive，標題「工作」開頭）分流進對應專案的 github repo。
**本機手動跑**（雲端 routine 讀不到本機 Drive 掛載，無法代勞）。

> **快速捕捉工具，下指令後一路處理完、禁中途問**。用戶用 `/inbox` 是為了快速紀錄想法/待辦；歸屬自行歸納判定，**不要停下用 AskUserQuestion 問**（要他確認＝浪費他時間，他自己標注更快）。標題式速記（正文空）是**多數常態**，不是異常，照常分流、別當問題回報。

## 前置：取本機資料

先讀 `~/.claude/wtf-root.txt` 取 `<WTF_ROOT>`，再執行：

```
python3 "<WTF_ROOT>/wtf-config/sync_config.py" inbox-info
```

（Windows 用 `python`）輸出 JSON：
- `clippings`：待掃資料夾；`ingested`：完成後移入處
- `pending`：Clippings 中「工作」開頭的檔名清單（＝待分流）
- `projects[]`：路由表，每筆 `{project, path（本機絕對路徑）, github, has_github}`

若 `vault` 為 `null` → 本機 `inbox-config.md` 未填路徑，**停下**告知用戶補 `wtf-config/inbox-config.md` 本機列。
若 `pending` 為空 → 回報「無待分流速記」，結束。

## 分流（逐檔）

對 `pending` 每個檔：

1. **讀** `<clippings>/<檔名>` 全文。
2. **判定目標專案**：依標題／內容（專案名、關鍵詞、人事物）對應 `projects[].project`，**自行歸納，不中途問用戶**。
   - 明確 → 該專案。
   - 多候選（如兩個同領域專案）→ 依關鍵詞／近期活躍度自行擇一，不問。
   - **真的判不出** → 目標設 `WTF_Under_Construction`，落地寫到其 `_context/INBOX.md`「（未分類）」區（留待用戶日後自行歸位）。
   - 多檔可不同專案。
   - **重複速記**（與先前已收錄同名/同內容）→ 不再寫入 INBOX，僅執行第 5 步移檔清掉。
3. **檢查 github**：目標專案 `has_github == false`（registry github 欄標「待確認」）→ **暫不分流**，列入「待補 github」清單，跳過此檔（原檔留 Clippings）。
4. **落地**：append 到 `<目標 path>/_context/INBOX.md`（無則建，開頭加 `# <專案> — Inbox`）。每筆格式：
   ```
   ## [YYYY-MM-DD] <原標題去掉「工作」前綴>
   <速記內文>

   _來源：Clippings/<檔名>_
   ```
   日期用今天（系統日）。
5. **移檔**：把原檔由 `<clippings>/` 移到 `<ingested>/`（用 shell `mv` / `move`，跨平台注意路徑引號）。

## 收尾：commit/push 各動到的專案

每個被寫入的專案 repo，切到其 `path`：

```
git -C "<path>" add _context/INBOX.md
git -C "<path>" commit -m "inbox: 收錄語音速記 N 筆"
git -C "<path>" pull --rebase && git -C "<path>" push
```

衝突即停、回報，不強推。Drive 鏡像專案若 `git -C` 報非 repo → 列入「待補 github」清單，該檔回退留 Clippings。

## 回報

- 分流：每筆「檔名 → 專案」
- 重複而未重收：清單
- 待補 github 而跳過：清單
- 各 repo commit/push 結果

> 共用 skill，真相源 `wtf-config/skills/inbox/`。改後各機 `python wtf-config/sync_config.py sync` 重新部署。
