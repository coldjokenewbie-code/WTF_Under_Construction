# Lessons Learned (實戰教訓)

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
