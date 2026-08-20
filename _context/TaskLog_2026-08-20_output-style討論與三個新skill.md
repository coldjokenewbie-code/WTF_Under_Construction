# TaskLog 2026-08-20 — output style 討論＋W_colab/index-this/resume-id-info 三個新 skill＋2TB SSD 選購協助

## 完成項目

1. **output style vs CLAUDE.md/AGENTS.md 強制力討論**：查證官方文件（code.claude.com/docs/en/output-styles）確認 output style 只改 system prompt，跟 CLAUDE.md 一樣純粹是提醒、無強制力；真正的強制力來自 hook。順手查出目前 Stop hook 鏈（`stop_dispatcher.py`）同時跑兩個檢查：`wtf-session-gate.py stop`（開場協議收據）與 `tools/ody/squad/stop_hook.py`（Tyrion 禁詞 lint，讀 `lint_rules.json`），確認兩者跟溝通風格搬去 output style 與否無關，不能省略。
2. **GLOBAL.md「交付即預覽」擴大範圍**：從原本限定網頁/HTML/圖表，擴大到文件/圖檔/影片/音檔皆比照辦理；影音明訂不可自動播放（改用 Finder/檔案總管顯示）；批次產出改開資料夾；`open` 統一補 `-g`（背景開啟，不搶前景）。
3. **新增 3 個 skill**：
   - `W_colab`（原名 `W_Doc_Guard`，使用者要求改名）：把 GLOBAL.md「共編檔鐵律」（`W_` 前綴檔案）落成操作化流程。
   - `index-this`：快速記內容進專案 INDEX.md，對應 GLOBAL.md「INDEX 鐵律」的決策點短記例外。
   - `resume-id-info`（原名 `mark-resume`，使用者要求改名）：工作中不想中斷（cmux 更新提醒、想獨立標出背景 session）時，手動把 `$CLAUDE_CODE_SESSION_ID` 記進當前 TaskLog，供之後任一新 session 手動接續；純手動、不做自動偵測。設計過程先討論了「自動偵測異常結束」方案，經使用者澄清情境其實是主動判斷、非異常偵測後，改為輕量純手動版本，且派 `claude-code-guide` agent 查證 Claude Code resume 機制（`--continue`/`--resume`/`/resume` 皆需手動觸發、crash 不影響 30 天內可撿回 transcript、SessionStart hook payload 帶 session_id）。
4. **2TB 行動SSD 選購協助**（非工程任務，附帶協助）：momo/pchome 搜尋比對，過程中發現 WebFetch 對 JS 動態載入價格的頁面抓取不可靠（同一頁面重複抓到不同數字，甚至抓到不存在的死連結 SanDisk E81 卻未先驗證就列出——使用者指正後補開頁確認排除）。最終給出 8 款「已開頁確認在架＋盡量重複驗證價格」的清單。

## 未解決問題／下一步

- ody squad dispatch 計畫（`/Users/coma/.claude/plans/swift-sauteeing-owl.md`）仍未動工。
- momo/pchome 選購清單中 Transcend ESD310C 2TB 連結的價格（$17,999）明顯偏離市場常態，疑似對到錯誤 SKU/組合包，未進一步查證，使用者若真要買這款建議自行現場核對。
- Kingston XS2000 2TB 價格只單次抓到，未重複驗證，可信度較低。

## 附記：本 session 內兩度發生「skill 改名 commit 漏帶內容」

`W_Doc_Guard→W_colab` 與 `mark-resume→resume-id-info` 兩次改名都發生同一個模式：`git mv` 後用 Edit 改 frontmatter/標題，隔了幾個工具呼叫（含跑 `sync_config.py sync`）才 `git add`+`commit`，結果 commit 裡的內容仍是改名前的舊版（`git show <commit>:<path>` 核對抓到），需要補一個 commit 修正。原因未完全查明（懷疑 rename-detection 顯示 RM 不代表內容真的一起進了 index，或工具呼叫序列間有時間差），**因應**：改名類操作後，一律用 `git show <commit>:<path> | head` 核對 commit 內容跟工作區一致，不能只看 `git status`/`git add` 沒報錯就當作成功。
