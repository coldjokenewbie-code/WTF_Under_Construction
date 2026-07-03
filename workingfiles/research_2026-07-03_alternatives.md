# 低成本「可商用」AI 圖像／影片方案橫向比價（Ideogram 與 ComfyUI 自架除外）

- 調查日期：2026-07-03
- 目的：使用者已有可用的 GCP Vertex AI（billing 已開），需橫向比價決定預算配置。
- 撰寫：Claude（deep-research 流程，多子代理分工 + 主線驗證）

---

## 0. 一句話結論

**圖像**：你手上的 Vertex AI「Gemini 2.5 Flash Image（Nano Banana）約 $0.039/張＋Google 官方 IP 賠償（indemnification）」已是「便宜＋商用風險最低」的組合，聚合平台上只有 FLUX.2 dev（~$0.012/MP）與 Qwen-Image（~$0.02/MP）名目上更便宜但無賠償保障；**影片**：Veo 3.1 Fast（~$0.15/秒）在「有官方賠償」的前提下已具競爭力，純看單價則 Seedance 1.5 Pro Fast（~$0.022/秒）與 Wan 2.6（~$0.07/秒）更低，但商用條款僅有搜尋摘要層級的佐證。

---

## 1. 重要方法聲明（先讀這段再用數字）

本 session 的對外 proxy 為**網域白名單制**：實測 `cloud.google.com`、`raw.githubusercontent.com`（及 GitHub API）**可以 WebFetch 實開**；`fal.ai`、`replicate.com`、`ai.google.dev`、`artificialanalysis.ai`、`docs.midjourney.com`、`kling.ai`、`minimax.io`、`runwayml.com`、`openai.com`、`huggingface.co`、`recraft.ai`、`web.archive.org` 等全部被 proxy 以 403 拒絕（已用 `$HTTPS_PROXY/__agentproxy/status` 診斷確認為政策拒絕）。

因此本報告的證據分三級：

| 證據等級 | 定義 |
|---|---|
| ✅ **實開驗證** | 官方頁面經 WebFetch 實際開啟讀過（僅限 Google 官方頁與 GitHub 上的授權全文） |
| 🔶 **交叉佐證（搜尋摘要，未實開）** | ≥2 個獨立來源的 WebSearch 摘要數字一致 |
| ⚠️ **單源線索（搜尋摘要，未實開）** | 只有單一來源，或來源之間互相矛盾 |
| ❌ **查不到** | 找過但無法取得可靠數字 |

**所有標 🔶/⚠️ 的價格在實際下單前，請人工開瀏覽器核對官方頁一次。**

---

## 2. 總對照表（方案 × 單價 × 商用條件 × 品質定位）

### 2a. 圖像

| 方案 | 單價（USD/張） | 商用條件 | 品質定位（一句話） | 證據 |
|---|---|---|---|---|
| **Vertex AI — Gemini 2.5 Flash Image（Nano Banana）** | $30/1M output tokens ≈ **$0.039**（1024²=1290 tokens） | 可商用；付費層資料不用於訓練；**列入 Google 生成式 AI IP 賠償清單** | 圖文合成、編輯一致性強；Google 主推的 Imagen 後繼者 | ✅ 價格實開驗證；賠償 🔶 |
| **Vertex AI — Gemini 3.1 Flash-Lite Image（Nano Banana 2 Lite）** | $30/1M ≈ **$0.039** | 同上 | 新一代輕量版 | ✅ 實開驗證 |
| **Vertex AI — Gemini 3.1 Flash Image（Nano Banana 2）** | $60/1M ≈ **$0.077** | 同上 | 新一代主力版 | ✅ 實開驗證（每張為推算） |
| **Vertex AI — Gemini 3 Pro Image（Nano Banana Pro）** | $120/1M ≈ **$0.155**（1K 圖；高解析更貴） | 同上 | 旗艦級，高解析、文字渲染強 | ✅ 實開驗證（每張為推算） |
| **Vertex AI — Imagen 4**（Fast/Standard/Ultra） | **$0.02 / $0.04 / $0.06** | 同上；⚠️ **已宣告棄用，2026-08-17 關閉**，官方導向 Gemini 2.5 Flash Image | 寫實攝影感強；已是退場產品 | 🔶 交叉佐證 |
| **Gemini API 免費層 — Gemini 2.5 Flash Image** | **$0**（摘要稱約 500 張/日，10 RPM） | **免費層可商用**，但輸入/輸出會被 Google 用於改進產品（含人工審閱）；服務 EEA/瑞士/UK 使用者必須用付費層 | 同 Nano Banana | 🔶 交叉佐證 |
| **fal.ai / Replicate — FLUX.2 [dev]** | ~**$0.012/MP** | 產出可商用（授權全文：Output 任何用途含商用，唯不得訓練競品模型）；權重自架商用需 BFL 付費授權，走 API 即合規 | 開放權重陣營畫質標竿 | 授權 ✅ 實開；價格 🔶 |
| **fal.ai / Replicate — FLUX1.1 [pro]** | ~**$0.04**（Ultra ~$0.06） | API-only；摘要稱 BFL API 條款允許個人與商業用途 | 寫實與細節強 | ⚠️ 單源線索 |
| **fal.ai / Replicate — FLUX.1 [dev]** | ~**$0.025–0.03** | 同 FLUX.2 dev 結構（產出可商用 ✅ 實開驗證） | 社群生態最大 | 授權 ✅；價格 🔶 |
| **Replicate — FLUX.1 [schnell]** | ~**$0.003** | **Apache 2.0**，自架/商用全開 | 快、便宜，品質次於 dev/pro | 授權 ✅；價格 ⚠️ |
| **fal.ai / Replicate — Seedream 4 / 4.5（ByteDance）** | ~**$0.03 / $0.04** | 轉售站聲稱產出可商用；**ByteDance 官方條款未能驗證** | 亞洲系寫實與美感強，版本迭代快 | 價格 🔶；條款 ❌ |
| **fal.ai — Qwen-Image（Alibaba）** | ~**$0.02/MP**（2.0 Pro ~$0.075/張） | GitHub repo **Apache 2.0**（✅ 實開）；HF 權重頁 license 欄未能驗證（推測同為 Apache 2.0） | 中文/文字渲染強 | 授權 repo ✅；價格 ⚠️（來源矛盾，最不可靠） |
| **fal.ai / Replicate — Recraft V3** | ~**$0.04**（向量 SVG ~$0.08） | 摘要稱：免費層**禁止商用**；付費/API 給完整所有權，且商用權以「生成當下方案」為準 | 設計/向量/品牌素材特化，SVG 輸出獨家 | 價格 🔶；條款 ⚠️ |
| **Midjourney** | 訂閱 **$10–120/月**（無 API） | 付費即可商用；**年營收 >$100 萬美元的公司須 Pro（$60）以上** | 藝術風格與美感標竿；無 API 是工作流硬傷 | 🔶 交叉佐證 |
| **Canva（Magic Media 等）** | Pro 約 **$15/月**（摘要） | 摘要稱免費層與 Pro 皆可商用 AI 產出；IP 賠償（Canva Shield）僅 Enterprise | 設計整合便利，模型品質非頂級 | ⚠️ 單源線索 |

### 2b. 影片

| 方案 | 單價（USD/秒） | 商用條件 | 品質定位（一句話） | 證據 |
|---|---|---|---|---|
| **Vertex AI / Gemini API — Veo 3.1** | Standard ~**$0.40**；Fast ~**$0.15**；另有 Lite ~$0.03–0.05（720p 無音訊）；Veo 3 舊價 $0.50（無音）/$0.75（含音） | 可商用；**列入 Google IP 賠償清單**；API 無免費層 | 西方陣營最強之一，原生音訊同步佳 | 🔶 交叉佐證 |
| **Kling 3.0（快手）** | 訂閱制：免費 66 credits/日；Standard **$6.99/月** 起（來源另有 $10 說法）；3.0 約 6–12 credits/秒 | **免費層禁止商用＋有浮水印**；Standard 以上含商用權 | 動作連貫與物理感強，AA 影片榜前段 | 🔶（Standard 價格來源矛盾） |
| **Hailuo / MiniMax（Hailuo 2.3）** | 訂閱 Standard **$9.99/月**（1000 credits，單支影片 15–80 credits）；API 以點數計，USD 換算查不到 | 免費層**不可商用**；付費層去浮水印＋商用權 | 人物動作與表演感強 | ⚠️ 單源（各來源層級混亂） |
| **Runway（Gen-4 / 4.5）** | Standard **$12/月**（年繳，625 credits）；Gen-4 約 10–15 credits/秒 → 粗估 **$0.19–0.29/秒** | **免費層無商用權**；實務上 Pro（$28/月）起才夠production 用 | 電影感與導演工具鏈完整 | 🔶 交叉佐證 |
| **Sora 2（OpenAI API）** | Standard **$0.10/秒**（720p）；Pro $0.30–0.70/秒；Batch 半價 | ⚠️ **消費版 app 已於 2026-04-26 停止；API 將於 2026-09-24 日落**——不建議新專案採用 | 敘事與物理模擬曾是標竿 | 🔶 交叉佐證 |
| **Wan 2.2 / 2.6（Alibaba）** | API（聚合平台）Wan 2.6 ~**$0.07/秒**（2K） | Wan 2.2 開放權重 **Apache 2.0**（✅ 授權全文實開驗證）→ 自架商用全開；API 版條款依平台 | 開放權重陣營最強影片模型 | 授權 ✅；價格 ⚠️ |
| **Seedance 1.5 Pro / 2.0（ByteDance）** | fal.ai：1.5 Pro Fast ~**$0.022/秒**、1.5 Pro ~$0.247/秒；2.0 已上 fal（2026-04） | 轉售/聚合平台稱可商用、無浮水印；ByteDance 官方條款未驗證 | AA 影片榜頂端常客（Seedance 2.0），性價比殺手 | 價格 ⚠️；條款 ❌ |

---

## 3. GCP Vertex AI 現價細節（你已有的資源）

### 3.1 圖像（✅ 官方頁實開驗證：cloud.google.com/vertex-ai/generative-ai/pricing）

| 模型 | 官方定價 | 每張推算（1024²=1290 tokens） |
|---|---|---|
| Gemini 2.5 Flash Image | $30 / 1M image output tokens | ≈ $0.039（頁面自註 ~$0.039） |
| Gemini 3.1 Flash-Lite Image（Nano Banana 2 Lite） | $30 / 1M | ≈ $0.039 |
| Gemini 3.1 Flash Image（Nano Banana 2） | $60 / 1M | ≈ $0.077 |
| Gemini 3 Pro Image（Nano Banana Pro） | $120 / 1M | ≈ $0.155（2K/4K 輸出 token 數更多、更貴） |
| Gemini 2.0 Flash Image Generation | $0.04 / 張（modality 計價） | $0.04 |

- 注意：Imagen 與 Veo 的定價**不在**該頁（該頁現稱「Agent Platform Pricing」，僅列 Gemini 系）；Imagen/Veo 價格為搜尋摘要交叉佐證。
- **Imagen 4（Fast $0.02 / Standard $0.04 / Ultra $0.06/張）已宣告棄用，2026-08-17 關閉服務**，Google 官方導向 Gemini 2.5 Flash Image（🔶 多來源一致：theplanettools.ai、intuitionlabs.ai、aipedia.wiki）。→ **不要再把預算規劃在 Imagen 上**。

### 3.2 影片（🔶 搜尋摘要交叉佐證）

- Veo 3.1 Standard ~$0.40/秒、Veo 3.1 Fast ~$0.15/秒（aifreeapi.com、mindstudio.ai、costgoat.com 多來源一致；標示為 2025-12 起的價格）。
- Veo 3.1 Lite ~$0.03–0.05/秒（720p、無音訊）（costgoat.com、veo3ai.io）。
- Veo 3（前代）：$0.50/秒（純影像）/$0.75/秒（含音訊），音訊加價約 50%。
- 4K 輸出有加價（~$0.30–0.60/秒，依層級）。⚠️ 各層級「含/不含音訊」的精確差價官方頁未能實開，**下單前請在 Vertex AI 控制台或官方定價頁核對一次**。

### 3.3 商用權與 IP 賠償

- Google Cloud 有「Generative AI Indemnified Services」官方頁（cloud.google.com/terms/generative-ai-indemnified-services，頁面存在、實開但內容截斷）；搜尋摘要明確指 **Imagen 與 Veo 均列入賠償清單**，賠償涵蓋兩層：(1) 未修改的生成產出被控侵權、(2) Google 訓練資料被控侵權（🔶 交叉佐證：Google Cloud Blog + synthedia）。
- 這是 Vertex AI 相對所有聚合平台/中國系模型的**獨有優勢**：出了版權糾紛 Google 出面賠。

### 3.4 Gemini API 免費層（AI Studio）

- 免費層 Gemini 2.5 Flash Image：摘要稱 10 RPM / 500 張/日 / 免綁卡（🔶 laozhang.ai、aifreeapi.com 一致）。
- Veo 影片生成：**API 無免費層**（🔶）。
- **免費層產出可商用**（🔶），但代價是：Google 會用你的輸入與產出「提供、改進與開發產品與機器學習技術」，**含人工審閱**；且若你的應用服務 EEA/瑞士/UK 使用者，條款要求只能用付費服務（🔶 ai.google.dev/gemini-api/terms 的摘要 + simonwillison.net 轉載）。
- → 實務判斷（**推測**）：免費層適合原型與內部素材；含商業機密的 prompt 或客戶案不要走免費層。

---

## 4. 授權逐字驗證結果（本次調查最高價值部分，全部 ✅ 實開）

| 模型 | 授權 | 關鍵條款（逐字驗證） | 來源 |
|---|---|---|---|
| FLUX.1 [dev] | BFL Non-Commercial License | 權重「僅限非商業用途」；但**產出可任何用途含商用**（"You may use Output for any purpose (including for commercial purposes)"），唯不得用產出訓練競品 | raw.githubusercontent.com/black-forest-labs/flux/main/model_licenses/LICENSE-FLUX1-dev |
| FLUX.2 [dev] | 同上結構 | 產出可商用（§2.d），同樣禁止訓練競品 | raw.githubusercontent.com/black-forest-labs/flux2/main/model_licenses/LICENSE-FLUX-DEV |
| FLUX.1 [schnell] | **Apache 2.0** | 自架、商用全開 | github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-schnell |
| Qwen-Image（repo） | **Apache 2.0** | 無商用限制（⚠️ 此為程式碼 repo；HF 權重頁未能開啟確認） | raw.githubusercontent.com/QwenLM/Qwen-Image/main/LICENSE |
| Wan 2.2 | **Apache 2.0** | 無商用限制，自架商用全開 | raw.githubusercontent.com/Wan-Video/Wan2.2/main/LICENSE.txt |

實務含義：**FLUX dev 系透過 fal.ai/Replicate 付費 API 呼叫（平台已向 BFL 取得商業授權）→ 產出商用合規**；自架權重做商業生成才需要另向 BFL 買授權。

---

## 5. 品質定位與公開評測

❌ **Artificial Analysis 排行榜無法實開**（artificialanalysis.ai 被 proxy 封鎖，HF Space 與 web.archive.org 備援也被封）。僅有搜尋摘要級訊號（**全部未驗證，僅供方向感**）：

- 圖像 arena 摘要：前五由 GPT Image 2（Elo ~1339）、Reve 2.0、MAI-Image-2.5、HiDream-O1-Image-1.5、GPT Image 1.5 佔據；AA 站上存在 FLUX.2 [max/dev/pro]、Seedream 4.0/4.5、Qwen Image 2.0 Pro、Recraft V4.1 的模型頁（代表這些家族均已有更新版本）。
- 影片榜摘要：中國系模型（Seedance 2.0 / Kling 3.0 / Wan 系）佔據含音訊 text-to-video 榜頂端；Veo 3.1 被描述為「最強西方選項」；Kling 3.0 1080p Pro 約第 5（Elo ~1106）。
- 通念級定位（訓練知識推測，未驗證）：Ideogram/Recraft 文字渲染與設計特化、FLUX 寫實與開放生態、Midjourney 藝術美感、Veo 音畫同步、Kling/Hailuo 動作物理。

---

## 6. 三欄總分類

### ✅ 確認的事實（官方頁/授權全文實開）
1. Gemini 影像模型 Vertex 定價：2.5 Flash Image $30/1M、3.1 Flash Image $60/1M、3.1 Flash-Lite $30/1M、3 Pro Image $120/1M image output tokens；2.0 Flash $0.04/張（cloud.google.com/vertex-ai/generative-ai/pricing）。
2. 1024² 圖 = 1290 output tokens → 2.5 Flash Image ≈ $0.039/張（同頁自註）。
3. Imagen 與 Veo 定價不在該頁（需另尋官方頁核對）。
4. FLUX.1 dev / FLUX.2 dev：產出可商用、權重自架非商業；schnell 與 Wan 2.2 與 Qwen-Image repo 為 Apache 2.0（GitHub 授權全文）。
5. Google「Generative AI Indemnified Services」官方條款頁存在。

### 🔶 交叉佐證的搜尋摘要（未實開官方頁，下單前需人工核對）
Imagen 4 三檔 $0.02/$0.04/$0.06 與 2026-08-17 關閉；Veo 3.1 $0.40（Std）/$0.15（Fast）/秒；Veo 3 $0.50/$0.75（無音/含音）；Imagen、Veo 列入 Google 賠償清單；Gemini API 免費層可商用但資料用於訓練＋人工審閱、EEA/UK 需付費層、2.5 Flash Image 免費 500 張/日；Sora 2 API $0.10/秒且 2026-09-24 日落；Midjourney $10/30/60/120 四檔＋年營收 >$1M 須 Pro 以上；Kling 免費層禁商用、Standard 起可商用；Runway 免費層禁商用、$12/月起；Seedream 4/4.5 ~$0.03/$0.04/張；Recraft V3 $0.04（raster）/$0.08（vector）。

### ⚠️ 單源線索或矛盾（可靠度低）
Kling Standard $6.99 vs $10/月（來源互斥）；Hailuo 訂閱各檔（來源層級混亂）；Qwen-Image 各平台價格（$0.005–0.075 亂到不能用）；FLUX1.1 pro $0.04、pro Ultra $0.06；Seedance 1.5 Pro Fast $0.022/秒、Wan 2.6 $0.07/秒；Canva Pro ~$15/月與 AI 產出商用條款。

### ❌ 查不到（已盡力，來源被 proxy 封鎖或根本沒有公開數字）
fal.ai/Replicate 任何一頁的官方標價原文；BFL API 服務條款原文（bfl.ai）；Recraft ToS 原文；ByteDance（Seedream/Seedance）官方商用條款；MiniMax API 點數→USD 換算；Artificial Analysis 排行的實際 Elo 與子項評比；Google 賠償條款頁全文；Canva 官方定價頁與 AI 條款原文。

---

## 7. 選型建議（推測層，基於上述事實）

1. **圖像主力：留在 Vertex AI，用 Gemini 2.5 Flash Image / 3.1 Flash-Lite（~$0.039/張）**。單價已貼近聚合平台低價帶，又獨有 Google IP 賠償與企業級條款；除非月產量極大，省下的 $0.01–0.02/張不值得放棄賠償保障。Imagen 4 即將關閉，勿再投入。
2. **設計/向量/文字排版特化需求**：Recraft V3（~$0.04，SVG $0.08）是唯一向量輸出，走付費 API 才有商用權——條款請先人工核對。
3. **極致省錢或需自架的圖像批量**：FLUX.1 schnell / Qwen-Image / Wan 2.2 皆 Apache 2.0（授權已逐字驗證），但這條路實質上就是 ComfyUI 自架路線的授權基礎。
4. **影片主力**：預算優先 → 先用 Veo 3.1 Fast（~$0.15/秒，有賠償）跑量、關鍵鏡頭上 Veo 3.1 Standard（~$0.40/秒）。想更便宜 → fal.ai 上的 Seedance（低至 ~$0.022/秒）或 Wan（~$0.07/秒），但商用條款只有轉售站聲稱，法務風險自負。
5. **避開**：Sora 2 API（2026-09-24 日落）；一切「免費層拿去商用」的做法（Kling/Runway/Hailuo/Recraft 免費層都明示或據稱禁商用；Gemini 免費層雖可商用但資料會被拿去訓練＋人工審閱）。
6. **Midjourney/Canva**：只有在你要它們的「風格」或「設計工作流」時才值得訂閱；按 API 工作流整合性它們是最弱的（Midjourney 無 API）。

---

## 8. 來源清單

### 實開驗證（WebFetch 成功）
- https://cloud.google.com/vertex-ai/generative-ai/pricing （Gemini 影像模型定價）
- https://cloud.google.com/terms/generative-ai-indemnified-services （頁面存在，內容截斷）
- https://raw.githubusercontent.com/black-forest-labs/flux/main/model_licenses/LICENSE-FLUX1-dev
- https://raw.githubusercontent.com/black-forest-labs/flux2/main/model_licenses/LICENSE-FLUX-DEV
- https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-schnell
- https://raw.githubusercontent.com/QwenLM/Qwen-Image/main/LICENSE
- https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/LICENSE.txt

### 搜尋摘要來源（未實開，proxy 封鎖）
- Imagen 4 價格與棄用：theplanettools.ai、intuitionlabs.ai、aipedia.wiki、mindstudio.ai
- Veo 3.1 價格：aifreeapi.com、costgoat.com、mindstudio.ai、veo3ai.io、unifically.com
- Google 賠償：cloud.google.com/blog（protecting-customers-with-generative-ai-indemnification）、synthedia.substack.com
- Gemini API 免費層條款：ai.google.dev/gemini-api/terms（摘要）、simonwillison.net、laozhang.ai、aifreeapi.com、remio.ai
- fal.ai/Replicate 模型價格：eesel.ai、evolink.ai、openrouter.ai 等聚合摘要
- Kling：eesel.ai、vo3ai.com、atlascloud.ai、checkthat.ai、evolink.ai
- Hailuo/MiniMax：felloai.com、magichour.ai、skywork.ai
- Runway：eesel.ai、checkthat.ai、propicked.com、fairstack.ai、somake.ai
- Sora 2：eesel.ai、costgoat.com、aifreeapi.com、cometapi.com、openrouter.ai
- Seedance/Wan：atlascloud.ai、fal.ai/seedance-2.0（僅搜尋標題）、gamsgo.com、evolink.ai
- Midjourney：docs.midjourney.com（僅搜尋摘要）、terms.law、eesel.ai、techjacksolutions.com、checkthat.ai
- Canva：搜尋摘要（canva.com/policies 系列頁被封鎖）
- Artificial Analysis：artificialanalysis.ai（被封鎖，僅搜尋摘要訊號）

### 需人工補驗的關鍵頁（開瀏覽器 5 分鐘可完成）
1. cloud.google.com/vertex-ai/generative-ai/pricing 的 Imagen/Veo 分頁（確認 Veo 3.1 各檔含/不含音訊差價）
2. cloud.google.com/terms/generative-ai-indemnified-services（確認 Imagen/Veo/Gemini image 在列）
3. fal.ai/pricing 與各 Replicate 模型頁「Run time and cost」
4. bfl.ai/legal/flux-api-service-terms（FLUX pro 系商用條款）
5. recraft.ai/legal/terms（免費 vs 付費商用權）
6. ai.google.dev/gemini-api/terms（免費層資料使用條款原文）
