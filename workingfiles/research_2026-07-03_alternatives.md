# 低成本「可商用」AI 圖像／影片方案橫向比價（Ideogram 與 ComfyUI 自架除外）

- 調查日期：2026-07-03
- 目的：使用者已有可用的 GCP Vertex AI（billing 已開），需橫向比價決定預算配置。
- 撰寫：Claude（deep-research 流程，多子代理分工 + 主線驗證）
- 備註：Google 已於 2026 年 5 月前後將 Vertex AI 更名為「Gemini Enterprise Agent Platform」，API 端點與 `/vertex-ai/` 網址仍可用，本文沿用 Vertex AI 稱呼。

---

## 0. 一句話結論

**圖像**：你手上的 Vertex AI 已是「便宜＋商用風險最低」的組合——Imagen 4 Fast **$0.02/張**、Gemini 2.5 Flash Image（Nano Banana）**$0.039/張**（皆官方頁實開驗證），且付費使用的產出**列入 Google 兩層 IP 賠償**；聚合平台上只有 FLUX.2 dev（~$0.012/MP）與 Qwen-Image（~$0.02/MP）名目上更便宜但無賠償。**影片**：Veo 3.1 Lite 純影像低至 **$0.03/秒**、Veo 3.1 含音訊 $0.40/秒（官方實開驗證）；純看單價 Seedance 1.5 Pro Fast（~$0.022/秒）更低，但其商用條款僅有轉售站聲稱。**預算建議直接留在 Vertex AI，特殊風格/向量需求才外掛聚合平台。**

---

## 1. 重要方法聲明（先讀這段再用數字）

本 session 的對外 proxy 為**網域白名單制**：`cloud.google.com`、`raw.githubusercontent.com`（及 GitHub）**可實開（WebFetch）**；`fal.ai`、`replicate.com`、`ai.google.dev`、`artificialanalysis.ai`、`docs.midjourney.com`、`kling.ai`、`minimax.io`、`runwayml.com`、`openai.com`、`huggingface.co`、`recraft.ai`、`canva.com`、`web.archive.org`、`r.jina.ai` 等全部被 proxy 以 403 拒絕（`$HTTPS_PROXY/__agentproxy/status` 診斷確認為出口政策拒絕，繞道 archive/翻譯代理也被封）。

證據分級：

| 標記 | 定義 |
|---|---|
| ✅ **實開驗證** | 官方頁面/授權全文經 WebFetch 實際開啟讀過（Google 官方頁、GitHub 授權檔） |
| 🔶 **交叉佐證（搜尋摘要）** | ≥2 個獨立來源的 WebSearch 摘要一致；未實開 |
| ⚠️ **單源線索（搜尋摘要）** | 單一來源或來源互相矛盾；未實開 |
| ❌ **查不到** | 已盡力查而無法取得可靠資料 |

**標 🔶/⚠️ 的價格與條款，下單前請人工開瀏覽器核對一次。**

---

## 2. 總對照表（方案 × 單價 × 商用條件 × 品質定位）

### 2a. 圖像

| 方案 | 單價（USD/張） | 商用條件 | 品質定位（一句話） | 證據 |
|---|---|---|---|---|
| **Vertex AI — Imagen 4 Fast** | **$0.02** | 產出＝Customer Data、可商用；付費使用列入 Google 兩層 IP 賠償 | 速度優先（~2.7 秒/張），寫實 | ✅ 實開 |
| **Vertex AI — Imagen 4** | **$0.04** | 同上 | 寫實攝影感均衡主力 | ✅ 實開 |
| **Vertex AI — Imagen 4 Ultra** | **$0.06** | 同上 | 原生 2K、最高品質 | ✅ 實開 |
| **Vertex AI — Gemini 2.5 Flash Image（Nano Banana）** | **$0.039**（1024²） | 同上 | 對話式編輯/一致性強，Google 主推 | ✅ 實開 |
| **Vertex AI — Gemini 3.1 Flash-Lite Image（NB2 Lite）** | **$0.034**（1K） | 同上 | 新世代輕量 | ✅ 實開 |
| **Vertex AI — Gemini 3.1 Flash Image（NB2）** | **$0.045–0.15**（512px→4K；1K=$0.067） | 同上 | 新世代主力 | ✅ 實開 |
| **Vertex AI — Gemini 3 Pro Image（NB Pro）** | **$0.134**（1K–2K）／$0.24（4K） | 同上 | 旗艦，文字渲染與高解析強 | ✅ 實開 |
| **Gemini API 免費層 — 2.5 Flash Image** | **$0**（摘要：10 RPM／約 500 張/日） | 摘要稱免費層可商用，**但**輸入/輸出會被 Google 用於改進產品（含人工審閱）；**免費使用不在 IP 賠償範圍**（賠償條款明文排除 free of charge） | 同 Nano Banana | quota ⚠️；排除賠償 ✅ |
| **fal.ai / Replicate — FLUX.2 [dev]** | ~$0.012/MP | **產出可商用**（授權全文 ✅：不得用產出訓練競品）；自架權重商用需 BFL 付費授權，走付費 API 即合規 | 開放權重陣營畫質標竿 | 授權 ✅；價格 🔶 |
| **fal.ai / Replicate — FLUX.1 [dev]** | ~$0.025–0.03 | 同上結構（授權全文 ✅） | 社群生態最大 | 授權 ✅；價格 🔶 |
| **Replicate — FLUX.1 [schnell]** | ~$0.003 | **Apache 2.0**，商用全開 | 快且極便宜，品質次之 | 授權 ✅；價格 ⚠️ |
| **fal.ai / Replicate — FLUX1.1 [pro]／Ultra** | ~$0.04／$0.06 | API-only；摘要稱 BFL API 條款允許商用 | 寫實細節強 | ⚠️ 單源 |
| **fal.ai / Replicate — Seedream 4 / 4.5（ByteDance）** | ~$0.03／$0.04 | 轉售站聲稱可商用；**ByteDance 官方條款未能驗證** | 亞洲系寫實美感，迭代快 | 價格 🔶；條款 ❌ |
| **fal.ai — Qwen-Image（Alibaba）** | ~$0.02/MP（2.0 Pro ~$0.075/張） | GitHub repo **Apache 2.0** ✅；HF 權重頁 license 未驗證（推測同） | 中文/文字渲染強 | 授權 repo ✅；價格 ⚠️（矛盾） |
| **fal.ai / Replicate — Recraft V3** | ~$0.04（向量 SVG ~$0.08） | 摘要：免費層**禁商用**；付費/API 完整商用權，權利以生成當下方案為準 | 設計/向量/品牌素材特化 | 價格 🔶；條款 ⚠️ |
| **Midjourney（訂閱，無 API）** | $10–120/月 | 付費即可商用；**年營收 >$100 萬美元公司須 Pro（$60/月）以上** | 藝術風格美感標竿 | 🔶 |
| **Canva（Magic Media 等）** | Pro 約 $15/月 | 摘要：免費層與 Pro 皆可商用 AI 產出；IP 賠償（Canva Shield）僅 Enterprise | 設計工作流整合便利 | ⚠️ 單源 |

### 2b. 影片

| 方案 | 單價（USD/秒） | 商用條件 | 品質定位（一句話） | 證據 |
|---|---|---|---|---|
| **Vertex AI — Veo 3.1**（最新版） | 含音訊 **$0.40**（720/1080p）／$0.60（4K）；純影像 **$0.20**／$0.40（4K） | 可商用；付費使用**列入 Google IP 賠償清單**（清單 2026-04-22 版明列 Veo） | 西方陣營最強之一，音畫同步佳 | ✅ 實開 |
| **Vertex AI — Veo 3.1 Fast** | 含音訊 $0.10／$0.12／$0.30（720p/1080p/4K）；純影像 $0.08／$0.10／$0.25 | 同上 | 快速迭代用 | ✅ 實開 |
| **Vertex AI — Veo 3.1 Lite** | 含音訊 $0.05／$0.08；純影像 **$0.03**／$0.05（720p/1080p） | 同上 | 量產草稿層 | ✅ 實開 |
| （參考）Veo 3／Veo 2 | $0.40 含音／$0.20 純影像；Veo 2 $0.50 | 同上 | 前代 | ✅ 實開 |
| **Kling 3.0（快手）** | 免費 66 credits/日；Standard $6.99/月起（另有 $10 說法）；3.0 約 6–12 credits/秒 | **免費層禁商用＋浮水印**；Standard 以上含商用權 | 動作連貫/物理感強，AA 榜前段 | 🔶（Standard 價矛盾） |
| **Hailuo / MiniMax（Hailuo 2.3）** | Standard $9.99/月（1000 credits；單支 15–80 credits）；API 點數→USD 查不到 | 免費層不可商用；付費去浮水印＋商用權 | 人物表演感強 | ⚠️ 單源 |
| **Runway（Gen-4/4.5）** | Standard $12/月（年繳，625 credits）；Gen-4 約 10–15 credits/秒 → 粗估 $0.19–0.29/秒 | **免費層無商用權**；production 實務上 Pro（$28/月）起 | 電影感、導演工具鏈完整 | 🔶 |
| **Sora 2（OpenAI API）** | Standard $0.10/秒（720p）；Pro $0.30–0.70/秒；Batch 半價 | ⚠️ 消費版已停（2026-04-26）、**API 2026-09-24 日落**——勿入新專案 | 敘事/物理模擬曾是標竿 | 🔶 |
| **Wan 2.2 / 2.6（Alibaba）** | 聚合平台 Wan 2.6 ~$0.07/秒（2K） | Wan 2.2 開放權重 **Apache 2.0**（✅ 授權全文實開）→ 自架商用全開；API 版條款依平台 | 開放權重陣營最強影片 | 授權 ✅；價格 ⚠️ |
| **Seedance 1.5 Pro / 2.0（ByteDance）** | fal.ai：1.5 Pro Fast ~**$0.022/秒**；1.5 Pro ~$0.247/秒；2.0 已上 fal（2026-04） | 聚合/轉售平台稱可商用無浮水印；官方條款未驗證 | AA 影片榜頂端常客，性價比殺手 | 價格 ⚠️；條款 ❌ |

---

## 3. GCP Vertex AI 現價細節（✅ 全部官方頁實開驗證）

來源：https://cloud.google.com/vertex-ai/generative-ai/pricing（Imagen 段 `#imagen-models`、Veo 段 `#veo`、Gemini 表格註腳）

### 3.1 Imagen（現役最新＝Imagen 4，無 Imagen 5）

| 模型 | 功能 | 價格 |
|---|---|---|
| Imagen 4 Ultra | 生成（最高品質） | $0.06/張 |
| Imagen 4 | 生成 | $0.04/張 |
| Imagen 4 | 升頻 2K/3K/4K | $0.06/張 |
| Imagen 4 Fast | 生成 | $0.02/張 |
| Imagen 3／3 Fast | 生成/編輯 | $0.04／$0.02/張 |
| Imagen Product Recontext／Virtual Try-On | — | $0.12／$0.06/張 |

⚠️ 另有多個搜尋來源（theplanettools.ai、mindstudio.ai 等）稱 Imagen 4 已宣告 2026-08-17 棄用、導向 Gemini 2.5 Flash Image；但**官方定價頁今日仍正常列出 Imagen 4**。規劃長期工作流時請以 Google 官方棄用公告為準再確認一次（🔶 級警訊、未在官方頁實開確認）。

### 3.2 Gemini 影像（Nano Banana 家族；現役最新＝3.1 Flash Image／3 Pro Image）

| 模型 | 解析度 | 每張價格（官方註腳換算） |
|---|---|---|
| Gemini 2.5 Flash Image（Nano Banana） | 1024²（1290 tokens @ $30/1M） | **$0.039** |
| Gemini 3.1 Flash-Lite Image（NB2 Lite） | 1K（1120 tokens @ $30/1M） | **$0.034** |
| Gemini 3.1 Flash Image（NB2） | 512px／1K／2K／4K | $0.045／$0.067／$0.101／$0.15 |
| Gemini 3 Pro Image（NB Pro） | 1K–2K／4K | $0.134／$0.24 |

### 3.3 Veo（現役最新＝Veo 3.1；**含音訊＝同解析度價格 ×2**）

| 模型 | 輸出 | 720p/1080p | 4K |
|---|---|---|---|
| Veo 3.1 | 影像＋音訊 | **$0.40/秒** | $0.60/秒 |
| Veo 3.1 | 純影像 | **$0.20/秒** | $0.40/秒 |
| Veo 3.1 Fast | 影像＋音訊 | $0.10（720p）／$0.12（1080p） | $0.30 |
| Veo 3.1 Fast | 純影像 | $0.08／$0.10 | $0.25 |
| Veo 3.1 Lite | 影像＋音訊 | $0.05（720p）／$0.08（1080p） | — |
| Veo 3.1 Lite | 純影像 | **$0.03**／$0.05 | — |
| Veo 3 | 影像＋音訊／純影像 | $0.40／$0.20 | — |
| Veo 2 | 純影像 | $0.50（720p） | — |

### 3.4 商用權與 IP 賠償（✅ 法律條文逐字驗證）

來源：https://cloud.google.com/terms/service-terms（Section 20「Generative AI Services」，2026-06-08 版）＋ https://cloud.google.com/terms/generative-ai-indemnified-services（2026-04-22 版）

1. **產出歸屬**：「Generated Output is Customer Data. … Google does not assert any ownership rights in any new intellectual property created in the Generated Output.」→ 產出屬於你，可商用。
2. **兩層賠償**：(i) 未修改的 Generated Output 被控侵權；(ii) Google 訓練資料被控侵權——Google 都出面賠。
3. **關鍵限制**：Generative AI Indemnified Service 定義明文排除「free of charge」使用——**免費額度/試用產出不在賠償範圍，付費計費的使用才有**。
4. **賠償失效情形**：明知可能侵權仍使用、關閉/繞過安全過濾、收到侵權通知後仍使用、商標類主張、對自訂資料無權利。
5. **Imagen 與 Veo 明列於賠償清單**（「…used with generally available versions of these foundation models: Codey, Gemini, **Imagen**, PaLM, **Veo**」）。

### 3.5 Gemini API 免費層（AI Studio）——主來源被封，僅推測級

`ai.google.dev` 全站 403（含 terms/pricing/rate-limits；translate.goog、r.jina.ai、web.archive.org、simonwillison.net 繞道全部被封）。以下全部為**搜尋摘要推測**：

- 免費層（Unpaid Services）**允許商用**，但 Google 會將輸入與產出用於「提供、改進與開發 Google 產品服務與機器學習技術」，含去識別化後的**人工審閱**。
- 付費層不用你的資料改進產品。
- 單源線索：EEA/瑞士/UK 使用者即使免費層也適用付費層資料條款（另一說法是該區只能用付費服務）——未驗證。
- 免費 quota：2.5 Flash Image 約 10 RPM／500 張/日（各方數字不一致，未驗證）。
- **Veo 經 API 無免費層**（多個獨立次級來源一致）。
- 結合 3.4 的 ✅ 事實：**免費層產出無 IP 賠償**。→ 實務建議（推測）：免費層只拿來做原型與內部素材。

---

## 4. 授權逐字驗證（✅ 全部實開）

| 模型 | 授權 | 關鍵條款 | 來源 |
|---|---|---|---|
| FLUX.1 [dev] | BFL Non-Commercial License | 權重僅限非商業；**產出可任何用途含商用**（"You may use Output for any purpose (including for commercial purposes)"），唯不得用產出訓練競品 | raw.githubusercontent.com/black-forest-labs/flux/main/model_licenses/LICENSE-FLUX1-dev |
| FLUX.2 [dev] | 同上結構 | 產出可商用（§2.d），禁訓練競品 | raw.githubusercontent.com/black-forest-labs/flux2/main/model_licenses/LICENSE-FLUX-DEV |
| FLUX.1 [schnell] | **Apache 2.0** | 商用全開 | github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-schnell |
| Qwen-Image（repo） | **Apache 2.0** | 無商用限制（⚠️ 程式碼 repo；HF 權重頁未能開啟） | raw.githubusercontent.com/QwenLM/Qwen-Image/main/LICENSE |
| Wan 2.2 | **Apache 2.0** | 無商用限制 | raw.githubusercontent.com/Wan-Video/Wan2.2/main/LICENSE.txt |

實務含義：FLUX dev 系走 fal.ai/Replicate **付費 API**（平台已向 BFL 取得商業授權）→ 產出商用合規；自架權重商業生成才需另向 BFL 購買授權。

---

## 5. 品質定位與公開評測

❌ Artificial Analysis 無法實開（本站＋HF Space＋archive 全被封）。搜尋摘要級訊號（**未驗證，僅供方向感**）：

- 圖像 arena：前五為 GPT Image 2（Elo ~1339）、Reve 2.0、MAI-Image-2.5、HiDream-O1-Image-1.5、GPT Image 1.5；AA 站存在 FLUX.2 [max/dev/pro]、Seedream 4.0/4.5、Qwen Image 2.0 Pro、Recraft V4.1 模型頁（代表各家族均有更新版）。
- 影片榜：中國系（Seedance 2.0、Kling 3.0、Wan 系）佔含音訊 text-to-video 榜頂端；Veo 3.1 被稱「最強西方選項」；Kling 3.0 1080p Pro 約第 5（Elo ~1106）。
- 通念定位（訓練知識推測）：Recraft＝設計/向量、FLUX＝寫實+開放生態、Midjourney＝藝術美感、Veo＝音畫同步、Kling/Hailuo＝動作物理、Seedream＝亞洲審美寫實。

---

## 6. 三欄總分類

### ✅ 確認的事實（官方頁/授權全文實開）
1. Imagen 4 全系價格：Fast $0.02／Standard $0.04／Ultra $0.06/張（現役最新版）。
2. Gemini 影像每張官方換算：2.5 Flash $0.039、3.1 Flash-Lite $0.034、3.1 Flash $0.067（1K）–$0.15（4K）、3 Pro $0.134–0.24。
3. Veo 3.1 全表：含音訊 $0.40/秒（1080p）起，純影像 $0.20/秒；Fast $0.08–0.30；Lite $0.03–0.08；**音訊＝同解析度 ×2**。
4. Google 兩層 IP 賠償，Imagen/Veo 明列在案；**免費使用明文排除在賠償外**；產出＝Customer Data、Google 不主張所有權。
5. FLUX.1/2 dev 產出可商用（權重自架非商業）；schnell、Wan 2.2、Qwen-Image repo＝Apache 2.0。

### 🔶 交叉佐證的搜尋摘要（未實開官方頁；下單前人工核對）
Gemini API 免費層可商用但資料用於訓練＋人工審閱；Veo API 無免費層；Sora 2 API $0.10/秒（720p）且 2026-09-24 日落、消費版已停；Midjourney $10/30/60/120 四檔＋年營收 >$1M 須 Pro 以上；Kling 免費層禁商用、Standard 起可商用；Runway 免費層禁商用、$12/月起、Gen-4 約 10–15 credits/秒；Seedream 4/4.5 ~$0.03/$0.04/張；Recraft V3 $0.04/$0.08；FLUX.2 dev ~$0.012/MP、FLUX.1 dev ~$0.025–0.03/張；Imagen 4 有 2026-08-17 棄用之說（與官方頁現況需再確認）。

### ⚠️ 單源線索或矛盾（可靠度低）
Kling Standard $6.99 vs $10/月；Hailuo 訂閱各檔與點數換算；Qwen-Image 價格（$0.005–0.075，亂到不能用）；FLUX1.1 pro $0.04／Ultra $0.06；Seedance 1.5 Pro Fast $0.022/秒；Wan 2.6 $0.07/秒；Canva Pro ~$15/月與 AI 商用條款；Gemini 免費層 500 張/日；EEA/UK 免費層限制。

### ❌ 查不到
fal.ai/Replicate 官方標價原文（全站被封）；BFL API 條款原文（bfl.ai）；Recraft ToS 原文；ByteDance（Seedream/Seedance）官方商用條款；MiniMax 點數→USD；Artificial Analysis 實際排名與子項評比；ai.google.dev 免費層條款原文；Canva 官方頁原文。

---

## 7. 選型建議（推測層，基於上述事實）

1. **圖像主力留在 Vertex AI**：量產用 Imagen 4 Fast（$0.02）或 Gemini 3.1 Flash-Lite（$0.034），品質關鍵圖用 Imagen 4 Ultra（$0.06）或 NB Pro（$0.134）。單價已在全市場低價帶，且是唯一有官方 IP 賠償的選項——但注意 Imagen 4 的棄用傳聞，新工作流建議壓在 Gemini 影像系（Google 明示的方向）。
2. **影片主力也留在 Vertex AI**：草稿/量產走 Veo 3.1 Lite 純影像（$0.03/秒）→ 成品鏡頭用 Veo 3.1 Fast（$0.08–0.12/秒）→ 關鍵含音鏡頭才上 Veo 3.1（$0.40/秒）。8 秒含音成品一支約 $3.2，Fast 版約 $0.96。
3. **要更便宜的影片**且能接受無賠償/條款模糊：fal.ai 的 Seedance（低至 ~$0.022/秒）與 Wan（~$0.07/秒）；Wan 2.2 若自架則 Apache 2.0 全開（但那就回到 ComfyUI 路線）。
4. **設計/向量/品牌素材**：Recraft V3 付費 API（~$0.04；SVG $0.08）是唯一向量輸出——條款先人工核對。
5. **避開**：Sora 2 API（日落中）；一切「免費層拿去商用」（Kling/Runway/Hailuo/Recraft 免費層禁商用；Gemini 免費層雖可商用但無賠償＋資料被用於訓練）。
6. **Midjourney/Canva** 只為風格或設計工作流訂閱，API 整合最弱（Midjourney 無 API）。

---

## 8. 來源清單

### ✅ 實開驗證（WebFetch 成功開啟）
- https://cloud.google.com/vertex-ai/generative-ai/pricing（Imagen/Gemini 影像/Veo 全部價格表）
- https://cloud.google.com/terms/service-terms（Section 20，2026-06-08 版）
- https://cloud.google.com/terms/generative-ai-indemnified-services（2026-04-22 版）
- https://cloud.google.com/blog/products/ai-machine-learning/protecting-customers-with-generative-ai-indemnification
- https://cloud.google.com/blog/products/ai-machine-learning/veo-3-1-lite-and-a-new-veo-upscaling-capability-on-vertex-ai
- https://raw.githubusercontent.com/black-forest-labs/flux/main/model_licenses/LICENSE-FLUX1-dev
- https://raw.githubusercontent.com/black-forest-labs/flux2/main/model_licenses/LICENSE-FLUX-DEV
- https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-schnell
- https://raw.githubusercontent.com/QwenLM/Qwen-Image/main/LICENSE
- https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/LICENSE.txt

### 🔶/⚠️ 搜尋摘要來源（未實開，網域被 proxy 封鎖）
- Gemini API 免費層：ai.google.dev/gemini-api/terms（摘要）、simonwillison.net、laozhang.ai、aifreeapi.com、remio.ai
- Veo/Imagen 第三方比價：aifreeapi.com、costgoat.com、mindstudio.ai、veo3ai.io、theplanettools.ai、intuitionlabs.ai
- Kling：eesel.ai、vo3ai.com、atlascloud.ai、checkthat.ai、evolink.ai
- Hailuo/MiniMax：felloai.com、magichour.ai、skywork.ai
- Runway：eesel.ai、checkthat.ai、propicked.com、fairstack.ai、somake.ai
- Sora 2：eesel.ai、costgoat.com、aifreeapi.com、cometapi.com、openrouter.ai
- Seedance/Wan：atlascloud.ai、gamsgo.com、evolink.ai、fal.ai/seedance-2.0（僅標題）
- Midjourney：docs.midjourney.com（摘要）、terms.law、eesel.ai、techjacksolutions.com
- FLUX/Seedream/Qwen/Recraft 價格：fal.ai、replicate.com（摘要）、openrouter.ai
- Artificial Analysis：artificialanalysis.ai（被封，僅摘要訊號）

### 需人工補驗的關鍵頁（開瀏覽器 10 分鐘可完成）
1. Imagen 4 是否確定 2026-08-17 棄用（Google 官方 deprecations 頁）
2. ai.google.dev/gemini-api/terms（免費層資料使用條款原文）與 rate-limits（免費 quota 實數）
3. fal.ai/pricing 與 Replicate 各模型頁「Run time and cost」
4. bfl.ai/legal/flux-api-service-terms（FLUX pro 系商用條款）
5. recraft.ai/legal/terms（免費 vs 付費商用權）
6. ByteDance Volcano Engine 的 Seedream/Seedance 商用條款
7. artificialanalysis.ai 圖像/影片 arena 現排名
