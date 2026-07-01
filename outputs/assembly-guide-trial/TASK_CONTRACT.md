# TASK_CONTRACT — 組立工場導覽 App 首頁「最棒 3 版」試做
> 立於動工前（harness 第一步）｜TL：Claude｜討論：Codex＋Antigravity｜2026-07-01

## 目標
組立工場博物館行動導覽 App「帶路」首頁，做 3 個明顯不同方向的最棒版本 + 研究/案例報告 + 為何最棒的簡報。手機直式、離線可跑、單檔 HTML（無外部素材）。

## Scope allowlist（只寫這裡，不動 Assembly 專案原檔）
- `outputs/assembly-guide-trial/v1_職人記憶.html`
- `outputs/assembly-guide-trial/v2_時光旅人.html`
- `outputs/assembly-guide-trial/v3_隨身指引.html`
- `outputs/assembly-guide-trial/報告與簡報.html`

## 「最棒」驗收標準（團隊定義，可視覺驗證）
1. 3 秒一眼是「帶路」而非展覽海報（老職工意象/指引語）
2. 主操作在單手拇指黃金區（螢幕下 1/3）
3. 音訊入口顯著（波形/呼吸動態，一鍵播放）
4. 無障礙：高對比、大字、觸控目標夠大
5. 情境時間智慧引導（下一場 14:30／40 分鐘必看）

## 要複製的參考動態
- Maps 底部卡片上滑 + 路徑流光箭頭（帶路指引）
- Spotify/AirPods 音波脈動（音訊優先）
- Find My 雷達波擴散（探索/任務）

## 三版定調
- V1 職人記憶：黑白線稿→彩色、音波呼吸播放鍵；情感最強
- V2 時光旅人：底部音訊膠囊＋路線卡、情境時間推薦；實用最強
- V3 隨身指引：大字高對比雙欄、雷達波擴散、無障礙；全齡/外國最友善

## 完成定義（coach 驗收才算完成）
- 3 版皆過視覺自驗：page_renders、no_broken_img、no_overflow（手機直式 390×844）
- 每版首屏截圖，逐條對上上面 5 條標準（目視）
- 報告含：最棒定義、參考動態、3 版截圖、為何這 3 個最棒
- 全程不問使用者；不動 Assembly 專案原檔（只寫本 allowlist）

## 前置授權評估
- A 計費 API：否　B 登入活站：否　C 連網/安裝：否（沿用既有 playwright，知識庫參考案例免連網）　D 動既有檔：否（只寫 WTF sandbox）　E 破壞性：否
- → 全清，無需授權，一路做完。
