---
name: skills-install
description: 將 WTF repo 的 skills 同步到當前專案或所有專案。用法：/skills-install（本專案）| /skills-install all（所有專案）| /skills-install update（預覽 diff 後安裝到本專案）
---

# Skills Install

將 WTF repo 的 `wtf-config/skills/` 同步到目標專案的 `._agents/skills/` 實體目錄，並自動建立 `.claude/skills/` 軟連結指向它。

來源路徑（固定）：
```
/Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/WTF_Under_Construction/wtf-config/skills/
```

---

## 模式說明

### `/skills-install`（預設）
安裝到**當前 working directory** 的 `._agents/skills/` 實體目錄，並建立軟連結相容性。

執行步驟：
1. 確認目標 `._agents/skills/` 實體目錄存在，不存在則建立。
2. `cp -r [來源]/. [當前專案]/._agents/skills/`
3. 建立軟連結相容性：確認專案層 `.claude/` 目率存在（不存在則建立），執行 `ln -s ../._agents/skills [當前專案]/.claude/skills`。
4. 回報：已安裝的 skill 清單、相容性軟連結狀態。

---

### `/skills-install all`
安裝到 `projects.md` 清單中**所有已知專案**，以及本機全域環境。

專案清單路徑：
```
/Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/WTF_Under_Construction/projects.md
```

本機路徑對應規則：專案名稱 → `/Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/[專案名稱]/`

執行步驟：
1. 讀取 `projects.md` 取得所有專案名稱。
2. 逐一對每個專案執行安裝（同預設模式）。
3. 同步全域：
   - Claude Code 全域：`~/.claude/skills/`
   - Codex 全域：`~/.codex/skills/`
   - Gemini 全域：`/Users/coma/Library/CloudStorage/GoogleDrive-coldjokenewbie@gmail.com/其他電腦/tachart_ihuy/Claude_cowork/projects/WTF_Under_Construction/wtf-config/skills/`（ symlink 維護）
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
- 不會覆蓋目標專案的 `.claude/CLAUDE.md` 或 `._agents/AGENT_SPEC.md`（專案設定各自獨立）。
- `projects.md` 中路徑不存在的專案會跳過並回報。
