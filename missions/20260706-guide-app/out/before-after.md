# guide-app before/after(2026-07-07 晨,Fable 接手紀錄)

## before(小隊,昨晚)
**零產出**。非能力判定——序列佇列一晚只到一棒,棒落在優先序 1 的 machine-report(該棒紀律合格)。guide-app 未被輪到。

## after(Fable 版 M1:開場頁)
- 產物:`開場頁_fable.html`+`shot_fable_開場頁.png`(390×844@2x,Playwright 實截)
- 機檢:0 pageerror/0 console error;click 互動斷言 OK;reduced-motion 支援;零 CDN。
- 過程紀錄:首版自審抓出 3 處版式缺陷(銘板直排字疊、kicker 折行、場次行斷字),兩輪修正後截圖複驗——**自己的產出同樣過鐵律,沒有豁免**。

## 錨點判定(算繪截圖 vs `outputs/assembly-guide-trial/final_claude_滿版.png`)
達正錨,超越點四項:
1. **真實資料接入**:15 站點數、14:00 場次「專家現場導覽:蒸汽機車秘辛」、三語 chips 皆來自 app 的 data/*.ts;錨版為靜態文案。
2. **語彙再深一層(錨-P2)**:CTA 做成機廠檢修吊牌形制(穿孔+牌身)、右緣直式「組立工場」銘板——裝飾元素可逐一追溯到題材;錨版按鈕為通用膠囊。
3. **三值紀律**:底部 scrim 壓到近黑、標題紙白、銅色唯一強調;層次比錨版更清(錨版中景偏糊)。
4. **可驗證性**:互動與錯誤皆有斷言鉤(`__ready`/`data-started`),錨版是靜圖。

未及之處(誠實):第二屏(上滑後)不存在——M1 範圍僅開場;Noto Serif TC 依賴系統字型,展機無則落 serif 預設(離線字體打包是 southlibrary 案的同型解,可移植)。

## 對小隊的後續對照協議
今晚小隊做 M2(導覽選單+站點內頁)時,**以本開場頁為新錨**:同語彙(銘板/掛牌/三值)、同資料源。屆時的 before/after=小隊 M2 頁 vs 本頁標準,那才是公平的能力對照(同題材、有錨可循)。
