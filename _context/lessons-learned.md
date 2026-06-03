# Lessons Learned (實戰教訓)

## 2026-06-03 (全域設定自動同步架構重整)

* **開場協議靠 hook，不靠 agent 自律**：CLAUDE.md 的「強制執行」依賴 agent 主動判斷，實踐中常跳過。唯一可靠方式：`settings.json` UserPromptSubmit hook 讓 harness 強制觸發，agent 無法繞過。hook 輸出透過 system-reminder 回報給 agent，agent 再向用戶確認。
* **Drive 路徑下 git pull 需先清 .lock**：Google Drive 同步 .git 會在 `refs/remotes/` 產生殘留 `.lock` 檔，導致 git pull 失敗。解法：pull 前 `find .git -name "*.lock" -delete`。已整合進 wtf-sync.sh。
* **機器專屬路徑的設定檔應放 repo，用 hostname:path 格式**：放在 `~/.claude/` 只有 Claude Code 能管理；放在 `wtf-config/extra-scan-dirs.txt` 加 `hostname:path` 格式，所有 agent 都能讀寫，各機器只套用自己那行。
* **AI 效能衰退的判斷與因應**：同一對話內發生事實歸因錯誤（把自己的提議誤記為用戶說的）屬能力衰退，不是正常波動。同一 model ID 不保證行為一致（可能靜默更新）。因應：降為執行層、關鍵狀態寫檔不依賴 AI 口述、開場協議改為用戶主動觸發、流程容錯優先。

## 2026-06-03 (skills 漂移整治與混合架構定案)

* **skills 採「混合架構」**：共用 skill（SSOT 11 個）只部署到全域 `~/.claude/skills/`（每台機器各一份實體副本，由 `sync_config.py sync` 維護），**不再複製進各專案 `.claude/skills/`**；專案層只放「專屬 skill」（如 data-verify、thumbnail-aware-images、remotion-best-practices）。理由：`sync_config.py` 從不同步專案層 skills，過去把共用 skill 複製進每個專案 → 各自過期成孤兒副本，是 skills 漂移的根因。
* **任何 skills/設定一律實體複製，禁止 symlink（再次踩雷確認）**：本次依舊版 `skills-install` skill 把專案 `.claude/skills` 改成 symlink，隨即發現違反既有鐵律——Drive/git 同步到 Windows 會變死檔。已全部還原為實體目錄。**過期的 skill/文件本身也會反過來誤導 agent**：修 SSOT 規則時，要連帶修「教學用的 skill 文件」（如 skills-install），否則下個 agent 照舊文又走錯。
* **Git_work（非 Drive 純 git 區）同樣適用無-symlink**：git 在 Mac 存實體目錄沒問題，但 Windows checkout 無權限時 symlink 會變文字檔。Git_work 各 repo 的共用 skill 已移除（靠全域），只留專屬。
* **zsh 不對未加引號變數做斷詞**：`for s in $VAR` 在 zsh（macOS 預設）不會把空白分隔的字串拆成多個詞，整串被當單一參數 → `rm -rf "$path/$VAR"` 靜默無效（有 -f 不報錯）。改用字面清單或陣列，或 `${=VAR}`。
* **`ai-team` 是共用 skill 的例外（範本＋就地實例）**：其 SKILL.md 規定專案文件（`AI_TEAM_DIVISION.md`/`AI_TEAM_WORKFLOW.md`/`agent-specs/*`）就地建在 `.claude/skills/ai-team/` 內。本次清理「共用副本」時整個刪掉 ai-team，連帶刪了 claude_CDIC_O4 的 7 支 Event agent-specs 與多專案填寫的 DIVISION/WORKFLOW（Git_work 已從 git 全數還原）。**教訓**：批次刪「共用 skill」前，先確認該 skill 資料夾內有無專案專屬巢狀檔；ai-team 這類「範本型」skill 在有客製的專案要整包保留。**Drive 區無 git，誤刪只能靠 Google Drive 網頁垃圾桶救**（約 30 天）——動 Drive 區檔案前更要先確認。
* **`sync_config.py` 全域部署用破壞性 rmtree，Windows 遇鎖定整批失敗**：`deploy_claude_dir()`（sync_config.py:174-181）對 `~/.claude/skills/` 做 `shutil.rmtree` 整批刪除再 `copytree`。Windows 上若任一 skill 資料夾被佔用（實測 ai-team 噴 `PermissionError WinError 5`，根因未驗證——推測編輯器/程序鎖定或防毒掃描），rmtree 中途失敗 → 全域 skills 整批沒部署（AGENTS.md 那段不受影響，照常寫 7 專案）。當下繞過法：單獨 `copytree` 目標 skill。**與 ai-team「絕不整包刪」是同一風險**：破壞性整批操作在 Drive／跨平台環境本就脆弱（同 symlink 失效、.git lock）。**修正方向（待施作）**：改逐 skill 就地覆蓋 `copytree(..., dirs_exist_ok=True)`，每 skill 包 try/except，單一鎖定只略過該項並回報，不毀全部；SSOT 已移除的舊 skill 再容錯刪除。此修正歸入 SSOT 同步架構討論的「階段一」（見 `workingfiles/SSOT同步架構討論_2026-06-03.md`）。

## 2026-06-02 (設定整合 T1/T6/T7 與結案規範)

* **寫新規則前先 grep 既有 skill/設定**：本次先在 GLOBAL.md 自訂「結案移 archive」與「WorkLog_」命名，事後才發現 `tasklog-naming` skill 早有「ClosedTaskLog_ 前綴」「TaskLog_」規範，造成兩處雙真相源衝突。新增任何規範前，先全域搜尋同主題是否已存在，否則必製造漂移。
* **「機械式」操作要驗證才算零歧義**：目錄改名 `output→outputs` 看似純機械，實則會打斷程式碼硬路徑引用（國圖南 `output/claude_layout/` 被 app.js/settings.json 引用）。凡涉及目錄改名/路徑，先 grep 引用再動，不可列入自動批次。
* **整理類腳本三段式安全**：report-only 稽核（`audit_structure.py`）→ dry-run 計畫（`organize_files.py` 預設）→ `--apply`。並把項目分 AUTO（機械零歧義，自動搬）/ MANUAL（成果vs素材等語意，只標記由人工拍板）。搬檔護欄：只搬不刪、同名不覆蓋、衝突跳過。
* **symlink 去中心化方案已被推翻**（修正 2026-05-24 lesson）：Drive 不支援跨平台 symlink，同步後變死檔。改為實體複製 + 同步腳本（`sync_config.py`）。任何新設計不再用 symlink。
* **Windows 主控台 cp950 中文亂碼**：Python 腳本輸出中文前加 `sys.stdout.reconfigure(encoding="utf-8")`，否則 print 出亂碼（檔案寫入用 utf-8 不受影響）。
* **交接待辦狀態用實況核對，別照單全收**：接手時前一份交接列「規則 commit 尚未執行」，實查 git log 發現交接後已有兩個 commit、working tree 乾淨＝該項已完成。交接文字是寫檔當下的快照，可能過時；接手第一步以 git/檔案實況驗證，不信任文件陳述（呼應 GLOBAL.md「關鍵狀態不依賴 AI 口述」）。

## 2026-05-24 (WTF 協作框架通用化與技能精簡)

* **去中心化與中立軟連結**：多 AI 代理協作時，將真實目錄命名為工具中立名稱（如 `_agents/skills`），並使代理預設目錄（如 `.claude/skills`）以軟連結（symlink）指向它，是實現去中心化與「唯一真理來源」的最優解。
* **溝通原則硬性限制**：在 `GLOBAL.md` 中寫入「禁止尊稱『您』」與「每次回應 300 字限制」，能有效約束 LLM 避免長篇大論、安撫討好與發散，顯著降低 token 開支。
* **開場提示一次性原則**：開場載入協議的「已載入設定」說明在同一個 session 中只需回報一次，後續問答應全面禁言該複本，直接進入對答。
* **技能共享與專案隔離混合架構**：為了避免專案獨有管理技能（如 `skills-prune`）混入全域同步目錄，專案層 `_agents/skills/` 應為實體資料夾，其中全域技能分別建立獨立 symlink，而專案獨有技能則直接以實體目錄隔離保存。
