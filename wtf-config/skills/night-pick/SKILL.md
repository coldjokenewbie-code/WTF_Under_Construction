---
name: night-pick
description: 選今晚雲端自主迴圈要跑的任務——掃本機專案提名 2-3 個候選，使用者核准後寫入 missions/QUEUE.md 並 push。下班前手動觸發（本機 CLI 專用，雲端/Cowork 不適用）。
---

# Night Pick：夜間任務選題棒

> 規格正本：`wtf-config/playbooks/mission-loop.md` 第 4.5 節。本 skill 是其可執行展開。
> 角色定位：**選題官只提名，不代決**——「值不值得做」是使用者的判斷。

## 步驟

1. **定位與更新**：讀 `~/.claude/wtf-root.txt` 取 `<WTF_ROOT>` → `git -C <WTF_ROOT> pull`。
2. **收集候選**（控制成本，不全掃）：
   - 讀 `<WTF_ROOT>/wtf-config/projects-registry.md`，取本機 hostname 的專案清單。
   - 每個專案只讀 `_context/INDEX.md` ＋ INDEX 指到的當前 TaskLog（三檔制）；從「未解決問題／下一步建議」段抽候選工作。專案多時派 haiku subagent 分攤，只收結論。
3. **掛載過濾（硬條件）**：候選所屬 repo 必須在 `playbooks/mission-loop.md` 第 6 節「雲端掛載清單」內；不在 → 剔除或標「僅限本機」另列。
4. **判準打分（四條全中才提名）**：
   - 影響大：解掉會讓後續工作變快或解鎖別的事。
   - 無阻塞：不需等使用者決策、外部資料或本機資源即可動工。
   - 可增量：切得成 ≤2 小時一棒的塊。
   - 低品味：驗收可機檢（測試/read-back/斷言），不吃美感判斷。
5. **提名**：列 2–3 個，每個一行格式：`<slug>｜<repo>｜一句話方向｜中了哪四條的理由`。四條全中的候選不足 2 個就照實說，不硬湊。
6. **等使用者核准**（明確說出要哪幾個＋優先序）。未核准前不寫檔。
7. **寫入佇列**：核准項寫入 `<WTF_ROOT>/missions/QUEUE.md` 佇列表（狀態欄=`待規劃`，整欄精確字串）→ `git add missions/QUEUE.md` → commit → push origin main；push 被拒 → `git pull --rebase`（衝突 `git rebase --abort` 回報需人工）後重推，最多 2 次。
8. **收尾回報**：一行「已排入 N 項，今晚 19:30 第一棒開跑；17:05 快報會推播進度」。

## 邊界

- 只在本機 CLI 跑（需 wtf-root.txt 與各專案本機路徑）；雲端 session 觸發本 skill 時改口頭建議候選、不寫檔。
- 不改 QUEUE 既有列、不動表頭與使用說明段（黃區，見 maintenance-protocol）。
