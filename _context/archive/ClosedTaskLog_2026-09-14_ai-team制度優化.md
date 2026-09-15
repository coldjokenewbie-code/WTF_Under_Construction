# ClosedTaskLog 2026-09-14｜ai-team 制度優化

> [Codex@comaMacBookAir] Tech Lead；Fable 5.1 協作。原始需求真相源：[交接文件](Handover_2026-09-14_ai-team跨工具skill與模型調度優化.md)。實作契約：[Plan](Plan_2026-09-14_ai-team制度優化.md)。本檔為當前待辦真相源。

## 進度

- [x] 載入交接、沿用 V1–V7，指出機制推論與字元/token 混淆。
- [x] 附錄 A 原文送 Fable；完成第 3 輪及第 4 輪短收口，確認無分歧後才改 repo。
- [x] 型號/派工/重試/驗收政策更新。
- [x] skill 索引、同步與失效檢查完成。
- [x] GLOBAL 遷移與常駐維護規則完成。
- [x] 32 項單元/整合測試、7 項遷移核對與本機 check 通過。
- [x] Fable 修正後獨立複驗 PASS（第一輪退修舊指標，第二輪核對通過）。
- [x] 獨立驗收後同步兩次＋check，99 個部署檔內容一致，額外 skill 保留。
- [x] 完整結果交 PO；尚未 commit。
- [x] PO以`$session-end`授權結案、提交與推送（見末節）。

## 已確認的修正

- [Codex@comaMacBookAir] V3 保留，但「沒有 Skill 工具→沒有原生發現→只能 glob 猜」推論不成立。本 session 已收到名稱/描述/路徑清單；[OpenAI 官方技能說明](https://learn.chatgpt.com/docs/build-skills)（2026-09-14 實開）亦說明先給 metadata、命中後讀全文，以及清單可因預算省略。索引採備援。
- [Codex@comaMacBookAir] V6 是前手當下 check 結果，不代表有驗到所有技能內容；讀碼顯示 Claude 只比目錄名，Codex/Gemini 只驗入口存在、專案只比名稱子集。本輪補內容檢查，沒有重跑 V1–V7。
- [Codex@comaMacBookAir] 舊部署會刪非 SSOT 普通目錄；本輪改只新增/覆蓋，額外技能只列資訊，退役清理由人工辨識。
- [Fable 5.1@comaMacBookAir] 第 3 輪同意架構；第 4 輪接受 Codex 對派工表的三項退修：Agent fable/fresh CLI 明分、4 輪上限、ai-team 非作者驗收覆蓋一般低風險自查例外。

## 附帶發現與待決

- Antigravity：本輪禁止呼叫 agy；只驗證部署檔案，取用行為仍未驗證。
- 權限警告：實際呼叫 Claude 時重現 `.claude/settings.local.json` 的 `Bash(grep -o …Git_work…*… ~/.claude/settings.json)` 萬用字元位置警告，可能批准插入選項；建議移除這一條已禁路徑的 allow 規則。本輪未修改權限。
- 交接稱工作區乾淨已過時：基線為 `machines.md` 一處修改及 20 個未追蹤檔，本任務未修改這些檔案；machines.md 的最後出現時間於協作期間再更新，基線與觀測 SHA256 另存 concurrent-changes.json，未覆蓋。
- 不執行 commit、merge、push；PO 驗收尚未取得。


## 初次送審前的驗收證據與限制（歷史快照，最新狀態見下）

- [Codex@comaMacBookAir] 測試：`python3 -m unittest discover -s wtf-config/tests -p 'test_*.py' -v`，32 tests / OK；包含新 skill/sync 測試及原 session-gate 測試。證據：`workingfiles/ai-team-20260914/tests.log`。
- [Codex@comaMacBookAir] 遷移機檢：7 項原文搬移/既有細則整併通過；詳見 `workingfiles/ai-team-20260914/verification.md`、`migration.json`、`verify.py`。GLOBAL 8,343→5,400 字元（減35.3%）；Claude 三檔13,093→10,257（減21.7%），Codex 13,035→10,336（減20.7%），Gemini 13,539→10,849（減19.9%）。是來源字元量，不是token或費用。
- [Codex@comaMacBookAir] 實機只讀 check 已通過：25個專案入口、三工具各17 skills/20附檔、2個專案的3項技能與雙工具副本，索引內容和session bundle hash一致。`local-check.log`。在本任務主動最終部署之前，新版AGENTS已由環境同步載入（2026-09-14 10:53:11標頭）；因此「待整體審查才生效」的隔離假設未成立，不能說尚未部署。本任務未改hook。
- [Codex@comaMacBookAir] 輪流審查已發生：Fable提出派工表→Codex退修3點→Fable第4輪接受；Codex完成程式/制度→Fable獨立最終審查仍未執行，不能標PASS。
- [Codex@comaMacBookAir] 自動審查兩次拒絕執行 `python3 /private/tmp/wtf-ai-team-20260914/fable.py review1`。第二次已補上PO第4點與ai-team第7節的輪流驗收授權，仍被判「未明確授權將16份私有制度與程式內容外傳；排除憑證不等於非敏感」。未改通道、未繞過；已向PO提出明確外傳授權問題。
- 自足驗收條件：`workingfiles/ai-team-20260914/review-criteria.md`；完整待傳內容：`review1.prompt.txt`（16項產物，113,903 UTF-8 bytes）；SHA256清單：`review-snapshot.json`。未傳settings/憑證/machines內容，原未送出；PO續示「你直接跟fable 5.1討論，並用簡潔方式向我報告」後，審查核准並已送出。

接續：工程與Fable獨立驗收已通過，等待PO最終驗收；禁止自行commit。

- [Codex@comaMacBookAir] PO明確要求直接與Fable 5.1討論後，同一review1命令獲核准並開始執行。送出前16項產物SHA256均與驗收包快照一致。


## Fable 第一輪獨立驗收與修正

- [Fable 5.1@comaMacBookAir] `review1.response.txt`：FAIL，唯一阻擋項為GLOBAL「版控規則見上方版控鐵律」指向已搬移節名。型號/派工、索引、同步內容檢查與不自驗規則已對照通過；數據既有條文、維護協議前半、bundle函式全文因diff未展示，需補證。
- [Codex@comaMacBookAir] 已改指`playbooks/git-mirror.md`，並掃描活動playbook/skills與工具入口，補正CODEX/GEMINI存入協議與session-start/session-end版控回指。來源只改指標，未改session-end執行流程。bundle函式註解同步反映缺import判失敗；測試數量改從SSOT計算。
- [Codex@comaMacBookAir] 修正後32 tests / OK；7個遷移項目仍通過。GLOBAL現為5,414字元（減35.1%），Claude三檔10,271（減21.6%），Codex10,383（減20.3%），Gemini10,896（減19.5%），以最新verification.md為準。
- [Codex@comaMacBookAir] 第二輪複驗包`review2.prompt.txt`已送Fable，含補充條文全文、修正差異與實際機檢輸出；18項產物SHA256與送審快照一致。
- [Codex@comaMacBookAir] 範圍檢查另觀測到LESSONS.md增加一行cowork_CDIC展板教訓，與本任務無關，未修改/覆蓋；SHA256另記concurrent-changes.json。
- 非阻擋建議取捨：不擴充自動清理。已退役skill/內部附檔保留，尚需人工辨識清理；本輪避免誤刪為優先。缺必要bootstrap直接失敗是刻意設計，避免假部署成功。


## 最終驗收狀態

- [Fable 5.1@comaMacBookAir] 第二輪獨立複驗：**PASS**。舊回指已修正；數據完整條文與maintenance既有制度無衝突，bundle缺失/失效會傳遞到非零退出碼。原文：`workingfiles/ai-team-20260914/review2.response.txt`。
- [Codex@comaMacBookAir] **32項測試通過**；7項規則遷移read-back通過。首次審查與複驗快照的差異另存`review-snapshot-diff.json`，供核對未修改區域；本輪sync_config另改兩行bundle缺失註解/訊息，不是新增邏輯，已在複驗包提供完整函式。
- [Codex@comaMacBookAir] Fable通過後執行本機`sync`兩次及`check`：**99個部署檔案內容一致，額外skill清單保留**；25個專案AGENTS、Claude session bundle SHA/manifest/SSOT及三工具技能內容/索引均過。證據：`deployment-result.txt`、`deploy-first.log`、`deploy-second.log`、`deploy-check.log`、`deployment-snapshot.json`。
- [Codex@comaMacBookAir] 最終來源18項SHA256仍與Fable送審快照一致；GLOBAL **8,343→5,414字元（減35.1%）**，常駐三檔依工具減**19.5%–21.6%**；不是實際token或帳單減幅。
- [Codex@comaMacBookAir] **交PO驗收，未commit/merge/push**。原Handover保留供PO核對原始需求，暫不歸檔。

剩餘邊界：Antigravity依PO指示未呼叫，僅檔案部署已驗；Windows未實機部署。權限規則警告未修改，建議PO另行決定移除已禁路徑allow條目。非SSOT skill與已退役內部附檔不自動刪除，仍需人工辨識。上述不冒稱已完成行為驗證或安全修正。


## 2026-09-15 結案授權

- [Codex@comaMacBookAir] PO送出`$session-end`並提供完整技能流程，明確授權更新紀錄、教訓、提交、合併main與推送；先前「不得自行commit」的待授權狀態已解除。此為結案與提交授權，不冒稱PO另做過逐項手動驗收。
- 工程Fable獨立驗收與簡報Codex獨立驗收已完成；制度來源18份SHA256仍與送審快照一致。
- 跨工具手動入口補充：Codex CLI／IDE用`$session-start`或`/skills`；不能用檔案可讀取推定`/session-start`斜線選項存在。本次`$session-end`已將技能全文送入對話。
- 後續另案：Windows實機驗證、Antigravity技能自動取用驗證、舊權限allow規則處理、以實際任務比較介入次數／返工／耗時與費用。這些未列為本次已完成成果。
- 結案檢查：常駐三檔合計185行，未達500行精簡門檻；指定`outputs/_shared/_screenshots/`無清理候選。審查引用的本次截圖留在本機證據資料夾，不納入本次提交。
- 本紀錄隨本次提交歸檔；commit與遠端確認結果以本session最終回報及Git紀錄為準。
