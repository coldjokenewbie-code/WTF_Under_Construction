# AI 額度儀表板與監控

2026-10-19 [Codex@Mac] Tech Lead；PO 三藏要求 ai-team 找 Claude 與 agy，追蹤三家額度、儀表板供檢查、各自監控便於調度。完成後 PO 驗收，不自行 commit。

## 證據與共識
- Claude /usage stream-json 的 assistant.usage_report.rate_limits.limits[] 已實測；查詢零生成 token。
- agy /usage json command.data.groups[].buckets[] 已實測；Gemini、第三方模型、Argon 分池。
- Codex app-server account/rateLimits/read 已實測；windowDurationMins 為準，primary 不一定5小時。只取白名單，不存accountId/creditId。
- Claude＋agy 第1至3輪皆完成，第三輪 GO。原文在 workingfiles/outputs/_shared/ai-usage-20261019/r{1,2,3}.{claude,agy}.txt。
- 方案與檢核表：同目錄 implementation_plan.md / task.md。
- 第一輪 Claude Sonnet 5 medium；agy 使用現有預設。第2/3輪 agy Gemini 3.8 Flash medium（查表與小範圍審查）；Codex 實作子代理 GPT-6.1 Sol medium（可測的資料/服務/UI）。高階 lead 僅診斷、規格與驗收。

## 待辦
- [x] 三家額度來源實測
- [x] 三輪討論達共識
- [x] 採集器、服務、儀表板完成
- [x] 單元/整合/實跑測試
- [x] Claude與agy輪流邏輯、視覺驗收
- [x] 啟動監控並讓三家實際查詢
- [x] 交付 PO 檢查；待 PO 驗收，尚未 commit

## 範圍與界線
只新增 tools/ai_usage、workingfiles/outputs/ai-usage-dashboard 與本案紀錄/證據。現有工作區其他未提交變更不動。每5分鐘官方查詢、10分鐘TTL，80/95/100警戒屬本機策略。供調度的check與監控不會自動付費、重置額度、切換帳號或廠商。未將檢查強制掛到所有既有session的全域hooks；整合方式隨交付說明。

## 交付與驗收證據
- 本機網址：http://127.0.0.1:8766；背景服務運作，三家均採集成功（Claude 3 池、Codex 1 池、agy 5 池）。
- `python3 -m unittest discover -s tools/ai_usage -p 'test_*.py'`：50 項通過。
- Playwright：375 / 768 / 1280 寬度無溢出、無頁面錯誤；證據 `ui-review-results.json`、`ui/final-*.png`。
- Claude 與 agy 三輪討論、資料契約邏輯審查及實際合成畫面視覺審查；兩家視覺均 PASS。原碼外傳曾遭自動審核拒絕，改由本機非作者代理獨立檢查完整原碼，修正後 PASS，無剩餘 P1/P2。
- 修正歷史依採樣時間判讀、同家派工鎖與待刷新標記、SIGTERM 子程序清理、任務結束前啟動採樣不可放行等問題，皆有測試。
- 三家經 `dispatch.py` 真實一句話測試均 exit 0，參見 `smoke-results.json`。任務後刷新遇冷卻會保留待更新標記，無新觀測不放行。
- 操作：`tools/ai_usage/README.md`；共同派工契約：`tools/ai_usage/AGENT_MONITORING.md`。
- 重開機須重新啟動；未安裝全域 hooks，只有本案派工入口強制守門。未 commit，未更動其他既有未提交檔案（開場機器登記除外）。

## 2026-10-22 重置數量與日期呈現
- PO 要求新增重置數量及到期日；每池新增完整含年份台北重置日期，保留倒數。非有效池日期標「上次取得」，缺失／非法時間標「尚未取得」。
- 目前接入資料僅有百分比與重置時間；絕對重置數量（token／次數）及訂閱到期日未取得，介面明示，不推算、不承諾到時自動補滿。
- 三輪討論由 Codex lead 與既有 service 執行代理完成；僅修改前端三檔，後端及派工規則不變。一般局部實作沿用既有執行層，主代理與 quota_discovery 非作者複驗。
- node --check 通過；Playwright 三尺寸及缺失、非法、過期、離線、停止、來源錯誤、採樣過期與倒數跨重置點均通過；獨立 diff 與三尺寸看圖 PASS。
- 計畫、原檔備份與驗收證據：workingfiles/outputs/_shared/ai-usage-reset-20261022/。未 commit。

## 2026-10-22 剩餘額度、週節奏與深色版
- PO 要求以剩餘額度呈現，參考圖片只作風格參考；後續指定預設黑暗模式。三家分欄圓環、歷史曲線、提示與門檻說明均改剩餘口徑；未知不畫成 0%，極小值與近滿值分別標 <0.1%／>99.9%。
- 每週池並列「額度剩餘／週期剩餘」對照條；≤24 小時重置且餘額≥20% 時提示安排既有合適工作；餘額落後時間比例≥15 百分點提示偏快，顯示實際差值及均勻分配參考。5 小時池、未知、過期及超週期時間不套週節奏。
- 今日判定採台北曆日；帳戶／供應商／額度池受限時抑制直接派工建議。無當日歷史證據不把本週消耗寫成今日消耗。原額度守門不變。
- 新增 pace.js；server.py 僅新增此精確靜態映射。已正常重啟既有監控服務，保留歷史資料；未變更採集、API 或派工政策。
- service 執行、Codex lead 與 quota_discovery 非作者輪流複驗；三輪討論與追加週節奏邊界共識完成。兩份 Playwright 驗收共 36 項通過，含三尺寸／深色／實際頁面／合成案例；19 項 monitor 測試通過。沙箱內測試不能綁埠，改於核准的本機測試環境通過；未降低瀏覽器 CSP。
- 證據與實作計畫：workingfiles/outputs/_shared/ai-usage-remaining-20261022/；邏輯與三尺寸看圖 PASS。交付仍是 http://127.0.0.1:8766/，未 commit。
