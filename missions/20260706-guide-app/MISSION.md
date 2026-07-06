# MISSION：guide-app（導覽 App 世界級視覺與體驗）
## 方向（一句話）
把組裝工廠導覽 App 的關鍵畫面提升到**世界級展覽品質**（視覺與體驗），以獨立 HTML 原型先行，實機整合後續本機做。

## 品質定位與錨點
- 對標 `wtf-config/anchors/展示頁面.md` 全部錨點：開場頁走錨-P1（滿版史料、文字退位）、導覽選單走錨-P3 資訊分層、全部過錨-P4 負錨清單。
- 「世界級」的操作定義：與 v4/final（`outputs/assembly-guide-trial/final_claude_滿版.png`，本 repo 內）並列不遜色，且比較句能指出本作**超越**該錨之處至少一項，否則只算「達正錨」。
- 評分鐵律遵 `anchors/README.md`；手勢與實機效能一律標「待實機驗」。

## 素材（唯讀）
repo `Assembly_Plant_Mobile_Guide`（React/TSX：App.tsx、components、data）。**repo 不可及→blocker 後結束本棒，禁 parked。**
本 repo 內可用：assembly-guide-trial 六版原型與定稿（同題材，直接沿用其視覺結論）。

## 產出位置
WTF `missions/20260706-guide-app/out/`：獨立 HTML 原型（開場頁、導覽選單頁、站點內頁各一）＋截圖對照。**原型不依賴 build，file:// 直開。**

## 硬底線
1. 零 CDN、零 console error（Playwright 斷言）。
2. 每頁截圖與錨點並列，比較句進 journal；未附截圖的頁面視為未做。
3. 動畫時序照 pitfalls-frontend 規範（等動畫完才互動）。
4. 內容用來源 repo 的真實站點資料，禁 lorem。

## Milestone
1. 開場頁原型達錨-P1＋截圖對照。
2. 導覽選單＋站點內頁原型達錨-P3＋截圖對照。
3. 三頁整合單一原型（頁間轉場）＋對抗審查＋「超越點」論證 → done。
