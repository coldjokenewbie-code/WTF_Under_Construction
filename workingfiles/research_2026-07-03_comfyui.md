# ComfyUI 免費/低成本產出可商用圖像與影片：可行路徑研究
> 日期：2026-07-03｜研究方法：WebSearch 搜尋 + WebFetch 實開官方頁面（本 session 網路 proxy 對多數外部網域回 403，**github.com / raw.githubusercontent.com 可正常實開**，故授權原文以官方 GitHub repo 的 LICENSE 檔為主要驗證來源；無法實開的一律標註「搜尋摘要，未實開驗證」）

## 一句話結論

**可行，而且路徑很明確**：ComfyUI 本體（GPL-3.0）不限制產出商用；選 Apache 2.0 授權的模型（圖像：FLUX.1 schnell、Qwen-Image；影片：Wan 2.1/2.2）就完全免費可商用；硬體上 MacBook Air 只能當「玩具級」試驗機，實際產能建議走雲端租 4090（約 US$0.2–0.4/hr），粗估每張圖成本 <US$0.01、每 5 秒影片約 US$0.02–0.05。

---

## 決策摘要（值不值得投入、跑在哪）

| 情境 | 建議 |
|---|---|
| 想先免費試玩、學 workflow | MacBook Air 裝 ComfyUI（官方支援 Apple Silicon），跑 SD 1.5 / SDXL / 量化 FLUX schnell，能動但慢 |
| 正式產圖（可商用） | 雲端 4090（RunPod/Vast.ai，~US$0.3/hr）+ FLUX.1 schnell 或 Qwen-Image（Apache 2.0），每張成本趨近零 |
| 正式產影片（可商用） | 雲端 4090 + Wan 2.1 (1.3B) 或 Wan 2.2 (TI2V-5B)（Apache 2.0）；高階需求才上 A100/H100 |
| Windows 桌機 | 取決於 GPU：≥8GB VRAM 可跑 SDXL 與 GGUF 量化 FLUX；≥24GB（如 4090）可跑 Wan 2.2 5B 影片。先查清楚 GPU 型號再決定 |
| 不想管維運 | Comfy Cloud（官方雲，credit 計費）或付費 API；但 FLUX dev 級 API 每張成本高一到兩個數量級 |

---

## A. 確認的事實（有實開來源佐證）

### A1. 軟體授權：ComfyUI 本體

| 項目 | 結論 | 來源（實開） |
|---|---|---|
| ComfyUI 授權 | **GPL-3.0**（GNU GPL Version 3, 29 June 2007，原文確認） | https://github.com/comfyanonymous/ComfyUI/blob/master/LICENSE |
| repo 歸屬 | 已在 Comfy-Org 組織下，仍標示 GPL-3.0 | https://github.com/comfyanonymous/ComfyUI |
| 產出可否商用 | GPL 約束的是「軟體本身的散布與修改」，不是產出圖片。核心協作者 ltdrdata 在官方 Discussion 表示：模型無授權限制時「產出的圖片不需要附加授權」 | https://github.com/comfyanonymous/ComfyUI/discussions/3804 |

**重要標註**：「GPL 不及於產出」在本次查證中只有 GitHub 討論串的**協作者個人意見**支撐（Discussion #3804、#14346），comfyanonymous 本人與 Comfy Org 官方書面聲明均查無；GNU 官方 FAQ 原文因 gnu.org 被 proxy 擋掉無法實開驗證。此為開源社群普遍理解，但引用時應註明是「社群法律理解」而非官方確認。

### A2. 圖像模型商用授權（截至 2026-07）

| 模型 | 授權 | 免費商用？ | 來源（實開） |
|---|---|---|---|
| **FLUX.1 schnell** | Apache 2.0 | **是，完全自由** | https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-schnell |
| **FLUX.1 dev** | FLUX.1 [dev] Non-Commercial License v1.1.1 | **模型使用限非商業**；但第 2(d) 條明文「You may use Output for any purpose (including for commercial purposes)」——**產出圖可商用**，唯不得用產出訓練競品模型 | https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-dev |
| **FLUX.1 Krea dev** | 同 FLUX.1 dev Non-Commercial License（GitHub flux repo 的 model_licenses 資料夾僅有 dev/schnell 兩份授權檔，Krea 適用 dev 授權） | 同 dev：模型限非商業、輸出可商用 | https://github.com/black-forest-labs/flux/tree/main/model_licenses ＋搜尋摘要交叉（bfl.ai blog、HF model card 列 flux-1-dev-non-commercial-license） |
| **SDXL** | CreativeML Open RAIL++-M | **是，無營收門檻**（僅 Attachment A 用途限制） | https://github.com/Stability-AI/generative-models/blob/main/model_licenses/LICENSE-SDXL1.0 |
| **SD 3.5**（Large/Medium/Turbo） | Stability AI Community License | **年營收 < US$1,000,000 免費商用**；超過須洽 Enterprise License | 原文：https://raw.githubusercontent.com/Stability-AI/stable-fast-3d/main/LICENSE.md（同一份 Community License 範本，含 US$1,000,000 條款）＋兩則獨立搜尋摘要一致（stability.ai 官網、官方 X 貼文） |
| **Qwen-Image** | Apache 2.0（20B MMDiT） | **是，完全自由**（不得使用阿里雲商標） | https://github.com/QwenLM/Qwen-Image （README 明文 "licensed under Apache 2.0"）＋ LICENSE 檔實開 |
| **HunyuanImage 3.0** | Tencent Hunyuan Community License | **可商用**，但：MAU > 1 億須另申請；**授權明文不適用於歐盟/英國/南韓**；不得用輸出改進其他 AI 模型 | https://github.com/Tencent-Hunyuan/HunyuanImage-3.0/blob/main/LICENSE |
| **Chroma**（lodestones，基於 schnell） | （搜尋摘要，未實開驗證）Apache 2.0，8.9B | 搜尋摘要稱可商用，**模型權重授權無法實開一手驗證**（HF 全域 403） | 搜尋摘要：HF lodestones/Chroma1-HD 等；周邊 repo https://github.com/lodestone-rock/ComfyUI_Chroma 標 Apache 2.0（僅節點工具，非權重授權證據） |

**FLUX dev 的實務注意（推測標註見 B 節）**：「模型只能非商業使用」與「輸出可商用」並存——為商業案子跑圖屬於「產生收入的活動」，落在授權排除的灰色地帶，保守做法是商用生產直接用 schnell/Qwen-Image，或買 BFL 授權。

### A3. 影片模型商用授權、VRAM 與速度（截至 2026-07）

| 模型 | 授權 | VRAM | 速度量級 | 來源（實開） |
|---|---|---|---|---|
| **Wan 2.1** | Apache 2.0（README 原文確認） | T2V-1.3B 僅 **8.19GB**；14B 約 76GB（offload 模式，官方表格為圖片無精確文字） | 1.3B 在 RTX 4090 生 5 秒 480P 約 **4 分鐘** | https://github.com/Wan-Video/Wan2.1 |
| **Wan 2.2** | Apache 2.0（LICENSE.txt 實開確認） | TI2V-5B 最低 **24GB（4090 可跑）**；A14B（MoE 27B/啟動14B）需 80GB | TI2V-5B 生 5 秒 720P@24fps **< 9 分鐘**（單張消費卡） | https://github.com/Wan-Video/Wan2.2 |
| **Wan 2.5** | **無開源權重**，僅阿里雲 API（官方 repo issue 無回應，HF 無權重） | — | — | https://github.com/Wan-Video/Wan2.2/issues/291 等（實開）；查不到開源授權 |
| **HunyuanVideo** | Tencent Hunyuan Community License：可商用、MAU>1億須申請、**排除歐盟/英國/南韓** | 官方最低 45GB（544p）/60GB（720p），建議 80GB | 720p/129幀/50步：單 GPU 約 1904 秒（~32 分）；8 GPU 約 338 秒 | https://github.com/Tencent-Hunyuan/HunyuanVideo ＋ LICENSE.txt 實開 |
| **LTX-Video** | 現行 repo **Apache 2.0**（LICENSE 實開）；後繼 **LTX-2** 改 LTX-2 Community License：**年營收 ≥ US$1,000 萬** 須付費商用授權，其餘免費商用 | 13B distilled LoRA 低至 1GB；RTX 4060 8GB 可 1 分鐘內生 720×480×121 | 13B distilled 在 H100 約 10 秒生成 HD；fp8 版近即時 | https://github.com/Lightricks/LTX-Video ；https://github.com/Lightricks/LTX-2 |
| **Mochi 1** | Apache 2.0（README 原文 "permissive Apache 2.0 license"） | 官方單 GPU 約 60GB（建議 H100）；README 明言 **ComfyUI 可優化到 <20GB** | 官方無公布生成時間（查不到） | https://github.com/genmoai/mochi |
| **CogVideoX** | 2B＝Apache 2.0；5B／1.5-5B＝CogVideoX License（學術免費；商用須至 open.bigmodel.cn 登記，免費但月訪問量上限 100 萬） | 2B：diffusers FP16 最低 4GB／INT8 3.6GB；5B：BF16 最低 5GB／INT8 4.4GB；1.5-5B：約 10GB | 2B 在 A100 約 180 秒；5B（5秒影片）A100 約 1000 秒、H100 約 550 秒 | https://github.com/zai-org/CogVideo ＋ https://raw.githubusercontent.com/zai-org/CogVideo/main/MODEL_LICENSE |

### A4. 圖像模型 VRAM 需求（搜尋摘要交叉，未實開官方頁）

多來源搜尋摘要一致（localaimaster、apatero、hardware-corner、city96 GGUF 頁、ComfyUI 官方 Discussion #4571）：

- **SDXL**：FP16 約 7–8GB → 8GB 卡可跑
- **FLUX.1 dev**：FP16 約 24GB；FP8 約 12GB；GGUF Q8 約 12.7GB；Q4_K_S 約 6.8GB（8GB 卡的實用下限，畫質略降）
- **FLUX dev 生成速度**：RTX 4090、1024²、20 步約 **15–30 秒/張**（Q8/FP8 約 15–18 秒；ComfyUI 官方 Discussion #4571 與 SaladCloud 實測一致）
- **Qwen-Image（20B）**：官方 README（實開）提及經 DiffSynth-Studio 逐層 offload + FP8 可低至 4GB VRAM 內推論（速度會大幅下降）
- **HunyuanImage 3.0**：官方 README（實開）：≥ 3×80GB —— **消費級硬體完全跑不動，自架路線可直接排除**

---

## B. 硬體與雲端成本

### B1. Apple Silicon / MacBook Air 可行性

| 事實 | 性質 | 來源 |
|---|---|---|
| ComfyUI 官方文件有 macOS（Apple Silicon M1–M4）安裝頁與 Desktop 版 | 官方支援（docs.comfy.org 頁面存在，內容為搜尋摘要，本 session 無法實開該站） | https://docs.comfy.org/installation/desktop/macos （搜尋摘要） |
| M4 Pro Mac mini 24GB 跑 FLUX 1024² 約 50 秒/張 | 使用者實測回報（搜尋摘要） | heyuan110.com 實測文 |
| 16GB RAM 可跑 SD1.5/SDXL/輕量 FLUX，約 10–40 秒/張；FLUX schnell 在 M1 Max 32GB 曾實測 19 分鐘/張（未優化） | 使用者實測回報（搜尋摘要） | medium.com/@tchpnk 系列文 |
| Mac 統一記憶體＝VRAM 共用池；16GB 機建議 GGUF Q4 + 量化 T5 | 使用者實測回報（搜尋摘要） | smartart.live、apatero.com |

**結論（推測標註）**：MacBook Air（無風扇、記憶體 8–24GB）可以安裝並跑 SD1.5/SDXL/量化 FLUX 學習 workflow，但速度慢（每張數十秒到數分鐘）、長時間生成會過熱降頻；**影片模型在 Air 上不實際**（動輒數十 GB 記憶體 + 數十分鐘運算）。定位：學習機/原型機，不是產能機。

### B2. 雲端時價（2026-07，搜尋摘要交叉；官方 pricing 頁被 proxy 擋、未能實開）

| 服務 | 價格 | 來源性質 |
|---|---|---|
| RunPod RTX 4090 | Community 約 **US$0.34/hr** 起（多個第三方比價站與官方頁摘要一致） | 搜尋摘要 ×≥2 |
| RunPod A100 80GB | Community 約 **US$1.89/hr**；Secure 加約 US$0.4/hr | 搜尋摘要 ×2 |
| Vast.ai RTX 4090 | 競價市場約 **US$0.17–0.44/hr**（浮動） | 搜尋摘要 ×2 |
| Google Colab | Pay-as-you-go US$9.99/100 運算單元（T4 約 57hr、A100 約 7hr）；Pro 約 US$9.99–11.99/月、Pro+ US$49.99/月；免費層 T4 不保證、單次上限 12hr | 搜尋摘要 ×2（兩站數字略有出入，Pro 標 $9.99 或 $11.99，標註不確定） |
| Comfy Cloud（官方雲） | 2025-12-08 起 credit 制：**0.39 credits/GPU 秒**，只計 workflow 實際執行時間；月費方案含 credit 池（具體美元定價查不到，官網被擋） | 搜尋摘要 ×2 |
| ComfyDeploy | per-invocation 計費；**具體價格查不到**（官網 pricing 被擋，搜尋摘要無數字） | 查不到 |
| BFL FLUX dev 商用授權 | Builder 級：自助購買、10K 張/月、單一網域商用、含微調/LoRA 權利；**具體月費金額查不到**（bfl.ai pricing 頁被擋） | 搜尋摘要（單源線索） |

### B3. 每張圖／每秒影片粗估成本（**推算**，非官方公布）

推算假設：雲端 4090 @ US$0.34/hr（RunPod Community 搜尋摘要價）；生成時間用上文已佐證數字。

| 產出 | 運算時間 | 推算成本 |
|---|---|---|
| FLUX.1 dev/schnell 1 張 1024²（Q8，~20 秒） | 20 秒 | **≈ US$0.002/張**（SaladCloud 實測「992 張/美元」≈ US$0.001，同一數量級，交叉吻合） |
| Wan 2.1 1.3B：5 秒 480P（~4 分鐘） | 240 秒 | **≈ US$0.023/支 ≈ US$0.005/影片秒** |
| Wan 2.2 TI2V-5B：5 秒 720P（<9 分鐘） | ≤540 秒 | **≈ US$0.05/支 ≈ US$0.01/影片秒** |
| HunyuanVideo 720p（需 A100/H100 級，~32 分鐘單卡） | 1904 秒 @ US$1.89/hr | ≈ US$1.0/支（5.4 秒片）≈ US$0.19/影片秒 |

**對比推論（推測）**：自架雲端路線的邊際成本比商業影片 API 低一到兩個數量級，但要自付「開機、載模型、除錯」的閒置時間與人力。

---

## C. 學習/維護成本誠實評估（定性，推測標註）

以下為根據搜尋到的實測文與社群討論所做的**定性評估**，非可量化事實：

1. **入門曲線**：節點式 workflow 概念 1–2 天可上手，但要穩定產出商用品質（ControlNet、LoRA、upscale、影片插幀）通常需數週實作累積。
2. **模型管理**：checkpoint/VAE/text encoder/LoRA 檔案動輒 5–25GB，版本與資料夾結構要自己管；量化版（GGUF）還需額外裝 ComfyUI-GGUF 自訂節點。
3. **更新踩坑**：自訂節點生態品質參差，ComfyUI 版本升級常弄壞舊 workflow（社群討論常見主題）；建議鎖版本、workflow JSON 進版控。
4. **雲端額外摩擦**：每次租機要拉模型（數十 GB），需用網路磁碟（RunPod network volume 另計費）或打包 Docker image，否則開機成本吃掉省下的錢。
5. **總結**：若每月產出量小（<100 張圖），付費 API 或 Comfy Cloud 更划算；量大或需要客製 pipeline（固定角色、品牌風格 LoRA）時，自架雲端 4090 路線的投資才會回本。

---

## D. 查不到清單（已盡查證義務）

| 項目 | 查過哪裡 |
|---|---|
| BFL FLUX dev 商用授權具體月費 | bfl.ai/pricing/licensing、help.bfl.ai（proxy 403）；搜尋摘要僅有方案名稱與內容物，無金額 |
| Chroma 模型權重授權一手原文 | HF lodestones 各路徑（403）、web.archive.org（工具不支援）；僅搜尋摘要稱 Apache 2.0 |
| Wan 2.5 開源授權 | 官方 GitHub issue（實開，無官方回覆）、HF Wan-AI 組織（無權重）——確認僅 API 服務 |
| Mochi 官方生成速度數字 | 官方 README 無此資訊 |
| Wan 14B/A14B 各 GPU 精確 VRAM 峰值 | 官方效能表為圖片格式，無法解析文字 |
| Comfy Cloud 具體美元月費、ComfyDeploy 價格 | comfy.org/cloud/pricing、app.comfydeploy.com（proxy 403）；搜尋摘要只有計費模式無完整價目 |
| comfyanonymous 本人對「GPL 與產出」的官方聲明 | 遍查官方 Issues/Discussions（#3804、#14346、#3362、#6508 均實開），無本人發言 |
| Comfy Org ToS 對產出歸屬的條款 | comfy.org/terms-of-service（403）；搜尋摘要稱「You exclusively own all Outputs」但未實開驗證 |

---

## E. 來源清單

### 實開驗證（WebFetch 成功打開原文）
- https://github.com/comfyanonymous/ComfyUI/blob/master/LICENSE （GPL-3.0）
- https://github.com/comfyanonymous/ComfyUI/discussions/3804 、/discussions/14346、/issues/3362、/discussions/6508
- https://github.com/black-forest-labs/flux/blob/main/model_licenses/LICENSE-FLUX1-dev 、LICENSE-FLUX1-schnell、model_licenses 資料夾
- https://github.com/Stability-AI/generative-models/blob/main/model_licenses/LICENSE-SDXL1.0
- https://raw.githubusercontent.com/Stability-AI/stable-fast-3d/main/LICENSE.md （Community License 原文含 US$1M 條款）
- https://github.com/Stability-AI/sd3.5 （code=MIT，模型授權另計）
- https://github.com/QwenLM/Qwen-Image
- https://github.com/Tencent-Hunyuan/HunyuanImage-3.0 ＋ /blob/main/LICENSE
- https://github.com/Tencent-Hunyuan/HunyuanVideo ＋ /blob/main/LICENSE.txt
- https://github.com/Wan-Video/Wan2.1 、https://github.com/Wan-Video/Wan2.2 ＋ LICENSE.txt、/issues/291
- https://github.com/Lightricks/LTX-Video 、https://github.com/Lightricks/LTX-2
- https://github.com/genmoai/mochi
- https://github.com/zai-org/CogVideo ＋ https://raw.githubusercontent.com/zai-org/CogVideo/main/MODEL_LICENSE

### 搜尋摘要（未實開，已交叉比對 ≥2 來源者於文中標明）
- runpod.io/pricing、vast.ai/pricing、colab.research.google.com/signup、comfy.org/cloud/pricing、blog.comfy.org（Comfy Cloud 計費）
- bfl.ai/licensing、help.bfl.ai（FLUX 商用授權方案）
- localaimaster.com、apatero.com、hardware-corner.net、willitrunai.com（FLUX/SDXL VRAM）
- github.com/comfyanonymous/ComfyUI/discussions/4571、blog.salad.com/flux-1-dev（4090 生成速度）
- medium.com/@tchpnk 系列、heyuan110.com、smartart.live（Apple Silicon 實測）
- docs.comfy.org/installation/desktop/macos（官方 macOS 支援頁存在性）
