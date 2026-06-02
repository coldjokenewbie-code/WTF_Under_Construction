# WorkLog 2026-06-02 — 程式 repo 移出 Drive 改純 git 管理

## 1. 本次完成項目
- **5 個程式 repo 從 Drive 移出**：`E:\Claude_cowork\projects\{Assembly_Plant_Mobile_Guide, Remotion_fun, claude_CDIC_O4, notebooklm-skill, Plnner2Line}` → `E:\Git_work\`。無損 rename，.git／remote 全保留。
  - 註：Assembly_Plant_Mobile_Guide 原為 Aseembly_Plant 的子資料夾，父層（文書）留在 Drive。
  - 搬移被 IDE 鎖檔（Antigravity IDE 23 行程 + node + codex 持有 handle），最終由使用者關閉程式後手動搬。
- **claude_CDIC_O4 損壞救援**：working tree 有 90 個檔被刪（含 `src/*.tsx` 程式碼、字型、圖片、影片），確認為 Drive 同步損壞、非人為。從 HEAD `git checkout` 全數還原（D=0）；3 個 M 檔（package.json 等）保留未動。
- **commit + push**：Remotion_fun(master)、Plnner2Line(main)、WTF_Under_Construction(main) 已推 GitHub。提交時排除垃圾檔（`AGENTS (1).md`、`out/`、`.pycache/`）。
- **全域設定 URL 修正**：`~/.claude/CLAUDE.md` 兩條失效 URL `claude-config/` → `wtf-config/`（`GLOBAL.md`、`CLAUDE_CODE.md`），curl 驗證皆 200。
- **cowork_CDIC 檔案整理**：AI script（.mjs/.js/.py）集中到 `tools/`（26 項）；散落截圖併入 `_screenshots/`（120 項）；`workingfiles/_scripts`、`_screenshots` 清空。根目錄產出檔（PNG/HTML/pptx）依使用者指示不動。

## 2. 未解決問題
- **P1｜notebooklm-skill 未推**：remote 為 `github.com/claude-world/notebooklm-skill`，無寫入權限。本機已 commit。待決定：fork 自己的 / 換 remote / 維持本機。
- **P1｜lesson-add 未寫入**：本次提議的 lesson（Drive 同步 .git 會損壞 repo）尚未寫進 `wtf-config/GLOBAL.md`，使用者跳至 /handover，待確認後補。
- **P2｜lesson-add skill 路徑過時**：skill 文件仍指 `claude-config/`，應改 `wtf-config/`（GLOBAL.md/CLAUDE_CODE.md/CLAUDE_COWORK.md）。
- **P2｜跨機 ~/.claude/CLAUDE.md**：本機檔，其他實體桌機若仍指舊 `claude-config/` URL 要各自改。
- **P2｜git push 分類器**：auto-mode 分類器會擋「直推預設分支」；settings.json 的 `autoMode.allow` 因 self-modification 護欄無法由 agent 自加。實務上使用者明確說「push」即放行。
- **P2｜E:\Git_work 跨機**：移出 Drive 後其他桌機需 `git clone` 取得這 5 個 repo。

## 3. 主要輸入檔案
- SSOT：`E:\Claude_cowork\projects\WTF_Under_Construction\wtf-config\`（GLOBAL.md、CLAUDE_CODE.md、AGENTS.md、sync_config.py、machines.md）
- 全域 bootstrap：`C:\Users\2025.DESKTOP-7SF21LR\.claude\CLAUDE.md`
- 前次交接：`_context/Handover_2026-06-02_工作區整合.md`（T1–T5 待辦來源）

## 4. 下一步建議
1. 確認並寫入 lesson（Drive×git 損壞）到 GLOBAL.md。
2. 修 lesson-add skill 的 claude-config→wtf-config 路徑。
3. 處理 notebooklm-skill remote 歸屬。
4. 接續前次交接 T2（skills 漂移）、T3（Drive 排除剩餘項）。
