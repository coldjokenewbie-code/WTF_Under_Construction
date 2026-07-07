# O4 開場影片配樂查證報告

查證日期：2026-07-08
範圍：Vertex AI Lyria（lyria-002）官方規格、其他長段音樂生成服務、envato 授權、loop 鋪底做法

## 重要限制先說明

本次查證環境的 WebFetch 工具網路存取被限制在極窄的白名單內，實測結果：
- 可開：`cloud.google.com`（僅 `/blog/...` 與 `/pricing/...` 等特定路徑）、`raw.githubusercontent.com`
- 不可開（多次重試、含 reader 代理 r.jina.ai 皆失敗，回傳 403）：`docs.cloud.google.com`（Lyria 正式 API 參考文件所在網域）、`ai.google.dev`、`deepmind.google`、`envato.com` 全系網域（含 `help.elements.envato.com`、`elements.envato.com`、`themeforest.net`）、`elevenlabs.io`、`stability.ai`、`stableaudio.com`、`suno.com`，甚至連 `en.wikipedia.org`、`npmjs.com` 這類一般網站都無法開啟。

換句話說：本環境目前**無法直接查證** Lyria 官方 API 參考頁（`docs.cloud.google.com/...`）、Lyria RealTime 詳細規格、envato/ElevenLabs/Stability/Suno 的官方授權條款頁。以下「事實」只列出實際 WebFetch 開啟成功並核對過內容的項目；查不到、或只在搜尋摘要出現但未能實開的項目一律移到「開放問題」，不當事實列入。

## 事實

1. **lyria-002 生成規格（部分）**：Google 官方範例 repo（GoogleCloudPlatform/generative-ai）的 Lyria 2 教學 notebook 顯示，呼叫 `.../publishers/google/models/lyria-002:predict` 時，輸出為 **30 秒 WAV 音檔，取樣率 48kHz**；可用參數為 `prompt`（必填）、`negative_prompt`（選填）、`sample_count`（選填，一次生成幾個版本）、`seed`（選填，與 `sample_count` 不可同時用）。notebook 內文沒有出現任何「延長／接續既有音訊（continuation/extend）」的說明或參數。
   來源：https://raw.githubusercontent.com/GoogleCloudPlatform/generative-ai/main/audio/music/getting-started/lyria2_music_generation.ipynb｜查證：實開頁面
   （注意：這是 Google 官方範例程式碼庫，不是 `docs.cloud.google.com` 上的正式 API 參考文件頁——後者本環境無法開啟，見開放問題。）

2. **Lyria 2 已在 Vertex AI GA（正式上線）**，官方部落格描述其可對「樂器、BPM 及其他特性」提供更精細的創作控制，可透過 Vertex AI Media Studio 或 Model API 存取。此文未提及最大時長、未提及「Create/Extend/Edit」三功能（這點只在其他來源的搜尋摘要看到，未經本次實開頁面證實，見開放問題）。
   來源：https://cloud.google.com/blog/products/ai-machine-learning/announcing-veo-3-imagen-4-and-lyria-2-on-vertex-ai｜查證：實開頁面

3. **Lyria（初代）企業版特性**：官方部落格說明生成音樂內建 SynthID 浮水印、有安全過濾機制、客戶資料不會被用於訓練模型，且 Google 對生成內容的第三方著作權爭議提供 indemnity（求償保障）。當時狀態為「Preview with allowlist」，需透過 Google 表單申請存取。
   來源：https://cloud.google.com/blog/products/ai-machine-learning/expanding-generative-media-for-enterprise-on-vertex-ai｜查證：實開頁面

4. **Lyria 3 與 Lyria 3 Pro（2026-04-07 發布，Public Preview）**：Lyria 3 可生成**最長 30 秒**的短片段音樂；Lyria 3 Pro 可生成**最長 3 分鐘**的完整編曲（含 intro/verse/chorus/bridge 結構）。兩者皆輸出高品質 stereo 音訊，內嵌 SynthID 浮水印並支援 C2PA 內容憑證。存取途徑為 Vertex AI API 與 Vertex AI Media Studio；Google Workspace／Google AI 訂閱戶另可透過 Google Vids 使用。此文未提及 lyria-002（舊版）的時長規格。
   來源：https://cloud.google.com/blog/products/ai-machine-learning/lyria-3-and-lyria-3-pro-on-vertex-ai｜查證：實開頁面

5. **官方定價頁未列出 Lyria 系列定價**：查了 Google Cloud 生成式 AI 定價頁與總價目表，皆搜尋不到「Lyria」相關的每次生成／每秒計價數字，只列出 Gemini 文字模型與部分 grounding 功能的價格。
   來源：https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing ｜查證：實開頁面（確認無 Lyria 項目）
   來源：https://cloud.google.com/pricing/list ｜查證：實開頁面（確認搜尋不到 Lyria 項目）

## 三路線對照

| 項目 | A) Lyria 單段連續生成 60s | B) 授權配樂庫（envato 等） | C) 單一質感 30s loop 鋪滿 60s |
|---|---|---|---|
| 可行性 | lyria-002 確認上限 30 秒（見事實1），不足 60 秒；Lyria 3 一樣 30 秒上限（事實4）。**唯一可能達成單次 60 秒的是 Lyria 3 Pro（最長 3 分鐘，事實4）**，但屬 2026-04 才發布的 Public Preview，能否申請、實際可用時長／穩定度未查證 | 技術上最直接可行：曲庫本身就有 60 秒以上成品可選 | 技術可行但非「連貫生成」，是生成後手動後製接合；Lyria 有無原生 loop／seamless 支援官方未查到說明（見開放問題） |
| 單次成本 | 官方定價頁未列 Lyria 費用（事實5），實際成本未知，需申請帳號後實測或洽 Sales | Envato Elements 為訂閱制、AudioJungle 為單曲購買制，實際金額本次未查（授權頁本身也開不了，見開放問題） | 與路線 A 相同，多一次後製工時但不需額外授權費 |
| 風險 | Lyria 3 Pro 為 Public Preview，非 GA，可能需申請 allowlist、配額/穩定性未知；lyria-002/Lyria2 是否支援 60 秒目前查無官方依據 | 授權條款是否涵蓋「政府機關展場循環播放」未能查證（envato 授權頁本環境開不了）；需人工二次確認是否要加購 broadcast/public display 授權 | 手動 crossfade 若接合處理不好，容易出現「接縫感」——這正是目前使用者打回的問題根源，路線 C 本質是繞過而非解決 |
| 預估工時 | 若 Lyria 3 Pro 可用：申請＋prompt 調整＋試聽，估 1 天內（含2-3輪修改） | 選曲＋版權確認，估半天至1天 | 生成＋後製 crossfade＋試聽迭代，估半天至1天，且需剪輯／DAW 工具與人工操作 |
| 依賴外部 | Vertex AI 專案權限、計費帳戶、Lyria 3 Pro preview access 申請 | Envato（或同類庫）訂閱／購買帳號、人工核對授權條款 | Vertex AI 帳戶（同路線A）＋音訊後製工具（Audacity/DAW等）＋人工操作 |

## 開放問題

以下項目本次查證環境無法實開官方頁面確認，需使用者或後續作業以一般瀏覽器人工查證，或改在不受限的網路環境重跑查證：

1. **lyria-002／Lyria 2 正式 API 參考文件**（`docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/lyria-music-generation` 等頁）本環境無法開啟，因此「是否支援 continuation／延長既有音訊」「BPM 參數是否可在 API 層直接設定」「lyria-002 在 Vertex AI 現行版本的正式時長上限（notebook 是 2026 前某時間點的範例，可能已更新）」三項，只有 notebook 層級的間接證據（事實1），沒有正式文件核對。**建議：使用者用自己的瀏覽器打開上述網址直接核對，或在 Vertex AI Console 建一個測試呼叫實測。**

2. **Lyria RealTime**（`ai.google.dev/gemini-api/docs/realtime-music-generation`、`deepmind.google/models/lyria/lyria-realtime/`）完全無法開啟。搜尋摘要顯示其為串流式生成、以 2 秒為單位延伸、session 上限約 10 分鐘，但這些數字**未經實開頁面核對，不可視為確認事實**。且 Lyria RealTime 是否屬於 Vertex AI（企業/政府可採購）還是僅 Gemini API 消費端產品，也需人工確認——這會影響「公部門展場影片能否合法商用」的判斷。

3. **Envato Elements / AudioJungle 授權條款**（`help.elements.envato.com`、`elements.envato.com`、`themeforest.net`、`envato.com`）全部無法開啟。搜尋摘要顯示 Elements 標準訂閱授權明確排除「broadcast」（電視/電台/串流），但摘要沒有清楚提到「政府機關展場現場螢幕循環播放（非電視/串流）」算不算 broadcast、需不需要另外的展示/公開播映授權。**這是路線 B 能否成立的關鍵未解問題，必須由使用者親自開瀏覽器查 license 頁，或直接寫信問 Envato 客服。**

4. **ElevenLabs Music、Stability Stable Audio、Suno/Udio** 的官方時長與商用授權頁（`elevenlabs.io/music-terms`、`stability.ai/license`、`suno.com/terms-of-service` 等）全部無法開啟。搜尋摘要提及 ElevenLabs Music 最長 5 分鐘、付費方案含商用授權；Stable Audio 最長約 3 分鐘、依營收門檻分社群/企業授權；Suno Pro/Premier 訂閱含商用權——但這些數字**均未經實開頁面核對**，只能列為「待查」，不列入事實或對照表的可行性判斷依據。

5. **Lyria 原生 loop／無縫循環支援**：官方文件未載明（在可查到的官方部落格與 notebook 中都沒有 loop 相關字樣）。搜尋摘要顯示業界慣例是用 crossfade 手動把生成的 30 秒素材頭尾接合，非 Lyria 原生功能——這點屬一般常識，非 Lyria 特定官方說法，僅供路線 C 工時估算參考。

6. **Lyria 3 Pro 申請流程與名額**：官方部落格只說是 Public Preview，沒有說明是否需要 allowlist 申請、審核時間、配額限制——若使用者要選路線 A，這是能否在期限內拿到存取權的關鍵未知數，需直接向 Google Cloud 業務窗口確認。
