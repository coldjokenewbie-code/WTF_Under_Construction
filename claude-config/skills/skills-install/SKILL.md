---
name: skills-install
description: 將 WTF repo 的 skills 同步到當前專案或所有專案。用法：/skills-install（本專案）| /skills-install all（所有專案）| /skills-install update（預覽 diff 後安裝到本專案）
---

# Skills Install

將 WTF repo 的 `claude-config/skills/` 同步到目標專案的 `.claude/skills/`。

來源路徑（固定）：
```
c:/Users/2025.DESKTOP-7SF21LR/Documents/Git_foler_anti/WTF_Under_Construction/claude-config/skills/
```

---

## 模式說明

### `/skills-install`（預設）
安裝到**當前 working directory** 的 `.claude/skills/`。

執行步驟：
1. 確認 `.claude/skills/` 存在，不存在則建立。
2. `cp -r [來源]/. [當前專案]/.claude/skills/`
3. 回報：已安裝的 skill 清單、是否為首次安裝或覆蓋更新。

---

### `/skills-install all`
安裝到 `projects.md` 清單中**所有已知專案**，以及 Claude 全域環境。

專案清單路徑：
```
c:/Users/2025.DESKTOP-7SF21LR/Documents/Git_foler_anti/WTF_Under_Construction/projects.md
```

本機路徑對應規則：專案名稱 → `c:/Users/2025.DESKTOP-7SF21LR/Documents/Git_foler_anti/[專案名稱]/`

執行步驟：
1. 讀取 `projects.md` 取得所有專案名稱。
2. 逐一對每個專案執行安裝（同預設模式）。
3. 同步 Claude 全域：`~/.claude/skills/`
4. 回報：每個專案的安裝結果（成功 / 路徑不存在跳過）。

---

### `/skills-install update`
預覽變更後，由用戶確認再安裝到**當前 working directory**。

執行步驟：
1. 對比來源與目標的每個 skill 目錄，找出差異（新增 / 修改 / 刪除）。
2. 使用 `diff -r --brief` 或逐檔比較，列出具體變更內容（哪個檔案、改了什麼）。
3. 向用戶簡報差異清單，**等待確認**。
4. 確認後執行安裝（同預設模式）。

---

## 備註
- 不會覆蓋目標專案的 `.claude/CLAUDE.md`（專案設定各自獨立）。
- `projects.md` 中路徑不存在的專案會跳過並回報。
