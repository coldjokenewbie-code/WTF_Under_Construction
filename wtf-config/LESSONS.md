# 全域 Lessons 索引（雲端 SSOT）

> 跨專案教訓的單一檢索入口。隨 git 同步至所有機器。
> **這是指標，不是副本**：每條只放「專案｜日期｜一句話｜連結」，完整內容留在工作層檔案，避免雙真相源。
> 工作層新增 lesson 後，須同步登錄一行到此表（見 `GLOBAL.md`「教訓兩層」）。
>
> 連結為相對路徑：Drive 專案自 `Claude_cowork` 根起算；WTF 自身已移出 Drive，連結標「（WTF repo）」者相對 WTF repo 根。

---

## 跨專案通用（高重用，優先參考）

| 專案 | 日期 | 一句話 | 連結 |
|---|---|---|---|
| WTF | 2026-06-09 | 判讀/指派工作紀律：①無證據絕不硬湊（找不到依據標「未知」交審，禁「挑個附近沒用到的」填值）②先建高對比/可追蹤檢視再判定（缺工具就肉眼瞎猜＝高錯誤）③鄰近≠連線、高信心幾何(端點距≈0)不得被肉眼印象推翻 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | 互動 HTML 交付前用 headless playwright 自驗（掛 pageerror/console listener+click 斷言互動），抓「畫面對但互動壞」；專案沒裝 playwright 走全域絕對路徑 require；file:// 開中文檔名先 URL-encode | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | ai-team cli-reference 按角色分段：各 agent 只讀自己那段（Codex TL/Antigravity TL/Claude TL），共用概念獨立一節，降低 context 耗費 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | sync_config.py deploy_other_tools() 只清 symlink、不清實體舊檔；換機/重裝後 stale 實體舊檔需手動清（已知 gap，待修）| `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | 禁止推測填入未實測的 agent CLI 規格（呼應誠實告知）：規格必須由當事 agent 實測或自報後再落檔，他方推測會把自己行為誤當對方的 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-08 | 雲端 routine 掃多 repo 只能靠 trigger 預掛載（直連 github 無憑證、clone 必敗）；registry 增刪要回 /schedule update 同步掛載；TZ=Asia/Taipei 定義「今日」避免 UTC 切日 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-07 | 技能載入：原生已自動列 skill 名稱+描述、body 觸發才讀；開場強讀全部 SKILL.md 是疊床架屋→廢除；「>10 數量門檻」隨成本消失一併撤，改以功能重疊為精簡準則 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-07 | 跨工具：各工具認自己原生檔名（Codex 讀 ~/.codex/AGENTS.md 非 CODEX.md，實證）、用實體副本非 symlink；per-machine 部署洞要 check 驗+寫對機待辦；三工具都有 headless CLI(claude -p/codex exec/agy --print)→ai-team 同機改 CLI 直驅、信號檔降 fallback | `_context/lessons-learned.md`（WTF repo） |
| 根 | 2026-05-03 | 七步驟工作流步驟4「執行不打擾」：卡關寫 `_blocker_*.md` 跳過，不中途問頁數/換工具 | `_context/lessons-learned.md` |
| 根 | 2026-05-03 | docx 註腳用 Word 頁尾 footnote，多次引用各生獨立 footnote，直改 `footnotes.xml` | `_context/lessons-learned.md` |
| WTF | 2026-06-03 | 整個 repo 移出雲端硬碟＞只 split 子目錄；前提變了（用戶已整包移出）就重評方案、別照交接照單執行 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | SSOT 檔禁寫單機絕對路徑；repo 一搬 `parents[N]`/`relative_to` 推導全崩，改絕對 registry/SCRIPT_DIR.parent | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | Drive 跨機協調檔：每機只寫自己的檔（單寫者免衝突）；禁掛常駐 tail -F（鎖檔擋 Drive 同步），改 on-demand 讀 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | 跨工具 skill 部署：實體複製到 codex/gemini，保留其自有 skill、不 prune；base 夾存在才部署（跨平台同碼） | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | 常駐 monitor 只在 ai-team+明示跨機討論才開；一般交棒靠更新 INDEX/TaskLog、對方新對話自然讀（非同步） | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-04 | 雲端 routine commit 死分支＝自動更新沒生效；要 pull--rebase→改→push main。雲端看不到本機 transcript，學習靠 git commit | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-04 | 雲端→用戶通知靠 NOTIFY 檔(nightly-notify.md)+session-start 浮出（wtf-root 錨點），零外部設定、漏不掉 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-04 | 跨工具部署：dangling symlink（舊架構死連結）被誤當工具自有保留、擋 copytree（Errno 17）；複製前拆同名 symlink。sync 報「寫入N個」N≠預期即沒全成 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | 技能精簡：規則型 skill 併回 GLOBAL.md、redundant 刪；移 skill 要清四處引用+git rm 後實體刪空目錄 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | Windows Python rmtree 被鎖(WinError5) 改 bash rm -rf 可繞過；MSYS symlink is_symlink() 不可靠靠 rmtree 守門 | `_context/lessons-learned.md`（WTF repo） |
| WTF | 2026-06-03 | 跨機 AI 協作＝共用檔案＋雙向 monitor（grep 限定 [TAG-R數字]、prev 設啟動基線避免自觸） | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-06-03 | Drive 同步 .git 跨機不可靠→各機自己 add、單一端 commit，另端 reset 淨空 index | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-06-03 | 設定檔自動執行 hook 屬自我修改，classifier 擋需用戶明授；破壞操作別繞過改靜態驗收 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-06-03 | sync_config.py 全域部署用破壞性 rmtree，Windows 遇 skill 鎖定（ai-team）整批失敗；改逐 skill 容錯覆蓋 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-06-02 | 接手時交接待辦狀態用 git/檔案實況核對，不照單全收文件陳述（可能過時） | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-05-24 | 溝通原則硬限制（禁「您」、回應字數上限）有效降 token、防發散 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-05-24 | 開場「已載入設定」一個 session 只報一次，後續直接進主題 | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| WTF | 2026-05-24 | ⚠️已被推翻：原 symlink 去中心化方案，因 Drive 不支援跨平台 symlink 改為實體同步（見 `sync_config.py`） | `projects/WTF_Under_Construction/_context/lessons-learned.md` |
| cowork_CDIC | 2026-05-21 | ⚠️已被推翻(2026-06-07)：Cowork 現可讀外部 URL（實測 fetch raw.githubusercontent 成功）→ Cowork 全域設定改填 CLAUDE_COWORK.md raw URL 自動載入，不再每次貼入 | `projects/cowork_CDIC/_context/lessons-learned.md` |
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
| cowork_CDIC | 2026-06-04 | 可微調文字位移用 margin 不用 transform：fill:both 進場動畫/translateY(-50%) 會壓過 inline transform | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-04 | SVG 裝飾網格灰點只能在 ≥2 線匯聚處：寫腳本點到線段距離測試驗證、新線平行既有方向、線端出血避免懸空 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-04 | File System Access 存檔報 user aborted＝取消選擇器非 bug；選同一檔允許寫入、handle 存 IndexedDB免重選 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | docx 同格雙語：deepcopy 中文段→換 w:t→addnext，保留 compress_type；⚠ 欄名可能與實際內容錯位，先看哪格有字 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | 新增同類元素避開既有編輯器固定計數(count:3)，改用獨立 class；白字配暗 text-shadow 提升淺底圖對比 | `_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | CJK 全形字寬≈1em、拉丁數字≈0.5em，「同字級≠同寬/同視覺」；兩行等寬須反向調字級，變動字數需 JS 動態算 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | 多行區塊跨欄 baseline 對齊：兩者用相同 line-height 行框 + Range.getClientRects 量 bottom、margin-top 微調校到 0-3px | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-05 | 「留白/靠上排列」常是設計取捨非 bug，先確認再動（自作主張改 flex 撐滿被否決） | `projects/cowork_CDIC/_context/lessons-learned.md` |
| WTF | 2026-06-05 | Session 啟動必須強制執行 wtf-config/sync_config.py check 與標準身分宣告，不可等用戶指示 | `_context/lessons-learned.md`（WTF repo） |
| cowork_CDIC | 2026-06-09 | 視覺驗收必須新舊疊圖 pixel-diff＋大面積純色定點取樣；只看新版好不好看會漏整片底色差(D區 P2/P5/P6 灰vs橘)；vision-based agent 漏純色差、像素取樣才抓得到；高頻照片區 diff% 是假象需 band 定位區分 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-09 | 「視覺僵硬」≠微調問題：根因常是版面構成（全左靠=行政表單感），AI 多輪微調救不回來；先根因診斷再換構圖重做一版；多 AI 獨立評比交叉驗證可提高 PO 採信度 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-09 | CSS/SVG 優於 mp4 做規矩進場動畫（淡入/描線/位移/序列）；mp4 代價：解析度鎖死/首屏等載入/字體烘焙/雙份維護漂移/autoplay 風險；mp4 真正出場=粒子/流體/3D/生成式光影/真實影片素材 | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-10 | PO 要放大/延伸既有視覺素材時禁自生成新藝術替換，沿用原素材「複製既有元素平移補位」延伸(波紋連退三次教訓) | `projects/cowork_CDIC/_context/lessons-learned.md` |
| cowork_CDIC | 2026-06-10 | 「任何方向都觸發副作用」需求當心邊界 early-return 吞掉它(解除暫停放邊界判斷前)；驗收要含邊界案例 | `projects/cowork_CDIC/_context/lessons-learned.md` |

---

## 專案專屬（詳見各專案 lessons-learned.md）

> 專屬細節不複製到此，僅列主題索引供發現。

| 專案 | 涵蓋主題 | 連結 |
|---|---|---|
| cowork_CDIC（CDIC 存保史料館） | 術語參照表優先、展品編號來源、年表整合、歷史照片來源、LibreOffice 渲染、素材主題真實相關、文案權威來源、三欄卡片版型、kiosk 互動、Playwright 視覺驗收、PPT QA 用 subagent、批次截圖固定寬、版面構圖診斷、CSS vs mp4 動畫判準、kiosk 簽名 canvas dpr cap | `projects/cowork_CDIC/_context/lessons-learned.md` |
| HsinchuSEC（科教館） | docx 多腳本執行順序（lxml 先字串後）、Word paraId 重生、雙螢幕截圖座標、FTE 與人頭數分標、面積非員額決定因素 | `projects/HsinchuScienceEducationCenter/_context/lessons-learned.md` |
| 國圖南（現正出版中） | PPT 頁碼會變動以內容為準、直書版面對位心法、字級名目pt≠render px、編輯模式存檔機制 | `projects/國圖南/_context/lessons-learned.md` |
| ppt_map_mark（PPT 拉線標註） | PPT COM 自動化匯出 PNG、跨頁底圖 bbox 座標對位（srcRect+group transform 正規化映射）、引線起點=文字實際結尾（Range/像素掃描）、定位法定案（染紅渲染+綠遮罩+td編號）、孤兒 pin 禁距離硬指派、工作紀律（無證據標未知/先建驗證視圖再判定） | `projects/ppt_map_mark/_context/lessons-learned.md` |

---

## 維護方式
- 工作中於各層 `_context/lessons-learned.md` 隨手記錄完整內容。
- 結案或 `session-end`／`lesson-add` 時，把新教訓濃縮成一行登錄本表。
- 高重用（跨專案可套用）放上區；專案專屬只在下區補主題關鍵字。
- 矛盾或過時條目標 `⚠️已被推翻` 並指向取代來源，不直接刪（保留歷史）。
