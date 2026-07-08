# journal:guide-app

## 2026-07-07 09:50 台北|Fable 接手棒(使用者授權的零產出接手)|進展:yes
做了什麼:M1 全項——開場頁原型(真實資料:15站/14:00場次/三語)、Playwright 截圖與互動斷言、錨點對照(達正錨+超越點四項,見 out/before-after.md)。首版自審抓 3 版式缺陷,兩輪修正後複驗。
證據:out/開場頁_fable.html、out/shot_fable_開場頁.png、out/before-after.md。
狀態:M1 界達成 → QUEUE 改「待核准」。今晚小隊 M2 以本頁為錨。
2026-07-08 01:02｜執行棒（主 session 代跑）｜guide-app：現況稽核完成（8路由/24截圖/16改善項），關鍵發現=Tailwind CDN 依賴（沙盒實證全掛→截圖需 CDN 本地化後重驗）、dark 主題從未啟用、動態僅一處；已補判讀：優化第一增量=Tailwind 本地建置｜進展 yes｜證據：out/ui-audit_2026-07-08.md、out/audit-screenshots/
2026-07-08 21:43｜執行棒（主 session 代跑）｜guide-app：第一增量之一完成——Tailwind CDN→本地建置（tailwindcss@3.4.19+postcss+autoprefixer，config 逐項承接原 inline 設定，視覺零改動）；JetBrains Mono 改自架 woff2（31KB variable font）取代 Google Fonts，Zen Maru Gothic 確認全專案未引用故直接移除；tsc 過＋vite build 過；順手修 playwright.config.ts port 誤植(5173→3000)解除 npm test 卡死。分支因 per-repo designated-branch 限制改用 claude/admiring-franklin-a1okxy（非 ui-uplift，比照 o4-soundtrack 前例），已推 origin(commit 1b79407)。手動 chromium 走 4 頁截圖存證（沙盒無 webkit 故官方 mobile-onsite/web project 測不了，環境限制非本棒回歸）｜進展 yes｜證據：Assembly_Plant_Mobile_Guide commit 1b79407；missions/20260706-guide-app/out/tailwind-local-20260708/{after_landing,after_map,after_schedule,after_exhibit}.png
chain-capability: FAIL（今晚 19:34 o4-soundtrack 首棒漏測，本棒補測）。複測 CronCreate：durable 參數描述仍明寫「Has no effect — durable persistence is not available. All jobs are session-only」，session 結束即消失，無法做到棒內自建下一顆 trigger 讓新 session 接手。與 07-07 判定一致，連續 PASS 計數仍為 0。
