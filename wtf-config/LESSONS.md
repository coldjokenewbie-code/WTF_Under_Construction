# 全域 Lessons 索引（雲端 SSOT）

> 跨專案教訓的單一檢索入口。隨 git 同步至所有機器。
> **這是指標，不是副本**：每條只放「專案｜日期｜一句話｜連結」，完整內容留在工作層檔案，避免雙真相源。
> 工作層新增 lesson 後，須同步登錄一行到此表（見 `GLOBAL.md`「教訓兩層」）。
>
> 連結為工作區相對路徑（自 `E:\Claude_cowork` 根起算）。

---

## 跨專案通用（高重用，優先參考）

| 專案 | 日期 | 一句話 | 連結 |
|---|---|---|---|
| 根 | 2026-05-03 | 七步驟工作流步驟4「執行不打擾」：卡關寫 `_blocker_*.md` 跳過，不中途問頁數/換工具 | `_context/lessons-learned.md` |
| 根 | 2026-05-03 | docx 註腳用 Word 頁尾 footnote，多次引用各生獨立 footnote，直改 `footnotes.xml` | `_context/lessons-learned.md` |
| WTF | 2026-05-24 | 溝通原則硬限制（禁「您」、回應字數上限）有效降 token、防發散 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-05-24 | 開場「已載入設定」一個 session 只報一次，後續直接進主題 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-05-24 | ⚠️已被推翻：原 symlink 去中心化方案，因 Drive 不支援跨平台 symlink 改為實體同步（見 `sync_config.py`） | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | Cowork 沙盒封鎖外網，外部 URL 一律標「（未驗證）」或請使用者瀏覽器確認 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | 分工：Cowork 讀寫本機/批次/長流程；Claude Chat 網頁瀏覽/WebSearch，互補不互換 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | 簡報/文件大綱先問實際過程再動筆，禁依主題名稱臆測內容 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | PRD 與 Prompt 功能不同不重複；Prompt 只放執行端所需，細節留 PRD | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | 專業術語以使用者提供定義為準，不自行推斷 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | WorkLog/Handover/lessons 三檔分工：做了什麼/接手做什麼/下次記得什麼 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | git commit 前查 `--cached --stat`，排除 node_modules/runtime/>100MB；超大檔 `git rm --cached` | `projects/cowork_CDIC/_context/lessons-learned.md` |
| HsinchuSEC | 2026-05 | 驗證不能只看腳本「Done」，必須截圖確認實際顯示才算驗收 | `projects/HsinchuScienceEducationCenter/_context/lessons-learned.md` |
| HsinchuSEC | 2026-05 | 論點必須有實際數字支撐，不可用結構推論代替數據 | `projects/HsinchuScienceEducationCenter/_context/lessons-learned.md` |
| 國圖南 | 2026-05 | 量不準先換手段：抽 pptx XML 會被 group transform 干擾，改算繪成圖再量測 | `projects/國圖南/_context/lessons-learned.md` |
| 國圖南 | 2026-05 | 並行 repo commit 只 stage 自己任務的檔，勿 `git add -A` | `projects/國圖南/_context/lessons-learned.md` |

---

## 專案專屬（詳見各專案 lessons-learned.md）

> 專屬細節不複製到此，僅列主題索引供發現。

| 專案 | 涵蓋主題 | 連結 |
|---|---|---|
| cowork_CDIC（CDIC 存保史料館） | 術語參照表優先、展品編號來源、年表整合、歷史照片來源、LibreOffice 渲染、素材主題真實相關、文案權威來源、三欄卡片版型、kiosk 互動、Playwright 視覺驗收、PPT QA 用 subagent、批次截圖固定寬 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| HsinchuSEC（科教館） | docx 多腳本執行順序（lxml 先字串後）、Word paraId 重生、雙螢幕截圖座標、FTE 與人頭數分標、面積非員額決定因素 | `projects/HsinchuScienceEducationCenter/_context/lessons-learned.md` |
| 國圖南（現正出版中） | PPT 頁碼會變動以內容為準、直書版面對位心法、字級名目pt≠render px、編輯模式存檔機制 | `projects/國圖南/_context/lessons-learned.md` |

---

## 維護方式
- 工作中於各層 `_context/lessons-learned.md` 隨手記錄完整內容。
- 結案或 `session-end`／`lesson-add` 時，把新教訓濃縮成一行登錄本表。
- 高重用（跨專案可套用）放上區；專案專屬只在下區補主題關鍵字。
- 矛盾或過時條目標 `⚠️已被推翻` 並指向取代來源，不直接刪（保留歷史）。
