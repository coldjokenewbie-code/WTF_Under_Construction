# Ideogram 商用圖像／影片生成調查（2026-07-03）

## 結論（一句話）
**部分完成（方法降級）**：WebFetch 在本環境結構性不可用（網路政策 403，經協調者確認），改用「WebSearch 多輪交叉佐證」標準完成調查；所有內容皆為**搜尋摘要，未實開驗證**，關鍵條款（尤其免費層可否商用）仍需人工開 ToS 原文核實。

## 決策摘要（回答問題本身）
1. **「Ideogram 4.0」確實存在**（多來源交叉佐證）：2026-06-03 發布，是 Ideogram 首個開放權重模型。但「免費拿權重自架＝免費商用」**不成立**——權重授權為非商用協議，只有推論程式碼是 Apache 2.0。
2. **免費/低成本取得可商用圖像的路徑**（按成本排序，皆待核實）：
   - ❌ 免費網頁方案：多數來源稱**僅限個人非商用**且產出強制公開——不建議商用。
   - ❌ 自架開源權重：權重授權明文非商用，商用需另談授權。
   - ✅ **API 按張計費（最低成本商用路徑）**：無月費，4.0 Turbo 每張 $0.03；一批 100 張商用圖約 $3。
   - ✅ 訂閱 Plus（月繳 $20／年繳 $15/月）：含商用授權、私人生成、每月 1,000 priority credits。
3. **影片生成：沒有**（三輪搜尋多來源一致）。Ideogram 含 4.0 皆為純靜態圖像模型，影片需下游接 Pika/Runway/CapCut 等工具。若工作流需要「一站式圖＋影片」，Ideogram 不符合，只能當圖像節點。

---

## 一、確認度分欄

> 標註規則：「交叉佐證」＝≥2 個獨立來源的搜尋摘要一致；「單源線索」＝僅一來源；全部皆為**搜尋摘要，未實開驗證**。

### A. 交叉佐證（搜尋摘要，未實開驗證）

**1. 模型版本與定位**
- Ideogram 4.0 於 2026-06-03 發布，為 Ideogram 首個開放權重（open-weight）文生圖模型；9.3B 參數 Diffusion Transformer，flow matching 訓練，原生 2048px，文字渲染基準（X-Omni English OCR）0.97，在開放權重模型中排名第一。
  - 來源：https://www.buildfastwithai.com/blogs/ideogram-4-open-weight-image-model 、https://www.3daistudio.com/blog/ideogram-4-open-image-model-explained 、https://techsy.io/en/blog/ideogram-4-0 、（官方頁存在佐證）https://ideogram.ai/blog/ideogram-4.0/ 、https://huggingface.co/ideogram-ai/ideogram-4-nf4
- 前代 Ideogram 3.0 於 2025 年 3 月發布（Style Reference、寫實強化）。
  - 來源：https://ideogram.ai/models/3.0/ 、https://learnprompting.org/blog/ideogram-3-0 、https://en.wikipedia.org/wiki/Ideogram_(text-to-image_model)

**2. 4.0 開源授權的關鍵陷阱**
- 推論程式碼＝Apache 2.0；**模型權重＝Ideogram Non-Commercial Model Agreement**（個人/研究免費，商用部署需另購授權；無營收門檻、無小商家豁免）。權重在 Hugging Face 上為 gated download。
  - 來源：https://huggingface.co/ideogram-ai/ideogram-4-nf4/blob/main/LICENSE.md （檔案存在佐證）、https://www.buildfastwithai.com/blogs/ideogram-4-open-weight-image-model 、https://mcp.directory/blog/ideogram-4-open-weight-image-model-2026 、https://evolink.ai/blog/ideogram-4-0-what-developers-should-know
  - 注意：第一輪搜尋摘要曾稱「open source under Apache 2.0」，後兩輪更細的摘要一致更正為「僅程式碼 Apache 2.0、權重非商用」。以後者為準，但**此點務必人工開 HF LICENSE.md 核實**。

**3. 免費方案**
- 產出**強制公開**（public gallery，他人可見 prompt 與圖），私人生成需 Plus 以上。
  - 來源：https://www.eesel.ai/blog/ideogram-pricing 、https://www.howdoiuseai.com/blog/2026-04-16-ideogram-free-tier-2026-what-you-get-and-limits 、https://docs.ideogram.ai/plans-and-pricing/available-plans （摘要）
- 免費層**僅限個人非商用**：兩輪不同查詢的摘要一致（"Free accounts allow only personal, non-commercial use"；"commercial use is not allowed on Ideogram's free tier"）。
  - 來源：https://sozee.ai/resources/ideogram-copyright-free-2026/ 、https://lilidi.ai/blog/ideogram-ai-for-business-understanding-commercial-licenses 、https://ideogram.ai/licensing/ （摘要）
  - ⚠️ 但存在矛盾說法，見第 C 節「兩說並陳」。

**4. 付費方案**（美元）
- Plus：月繳 $20／年繳 $15/月（省 25%）；1,000 priority credits/月＋unlimited slow credits、private generation、image upload、自訂色盤、商用授權。
  - 來源：https://checkthat.ai/brands/ideogram/pricing 、https://www.eesel.ai/blog/ideogram-pricing 、https://fluxnote.io/guides/ideogram-pricing-guide-2026
- Pro：月繳 $60／年繳 $42/月（省 30%）；3,500 priority credits/月、批次生成（CSV 上傳）。
  - 來源：https://checkthat.ai/brands/ideogram/pricing 、https://www.eesel.ai/blog/ideogram-pricing
- 免費：$0，每週 10 slow credits（額度數字有矛盾，見 C 節）。

**5. API 定價**（每張圖，flat fee，回傳 4 張＝4 倍）
- 4.0：Turbo $0.03／Default $0.06／Quality $0.10（兩輪獨立查詢摘要完全一致）
- 3.0：Turbo $0.03／Default $0.06／Quality $0.09
- 舊模型：2a Turbo $0.025、1.0 Turbo $0.02（兩次查詢皆出現，但可能同源自 costbench，佐證力較弱）
  - 來源：https://ideogram.ai/api-pricing/ （摘要）、https://developer.puter.com/tutorials/ideogram-api-pricing/ 、https://costbench.com/software/ai-image-generators/ideogram/ 、https://www.eesel.ai/blog/ideogram-pricing

**6. 商用授權條款（ToS 摘要）**
- Ideogram 不主張 User Output 所有權，付費用戶可商用；例外：不得用產出訓練與 Ideogram 競爭的模型；使用者須自行負責第三方權利（Ideogram 明文免責）。
  - 來源：https://ideogram.ai/legal/tos （摘要）、https://conductatlas.com/platform/ideogram/ideogram-terms-of-service/ 、https://sozee.ai/resources/ideogram-copyright-free-2026/

**7. 影片生成：無**
- 三輪查詢、多個獨立來源一致：Ideogram（含 4.0）為純靜態圖像模型，無任何原生影片/動畫/動態功能；motion 內容需下游接 Pika、Runway、CapCut、DaVinci Resolve 等。
  - 來源：https://fluxnote.io/guides/how-to-turn-ideogram-image-into-video 、https://vidmuse.ai/blog/ideogram-4-0 、https://filmora.wondershare.com/trending-topic/ideogram-ai.html

**8. 強項與弱項**
- 強項（多來源一致）：圖內文字渲染準確度業界頂尖（測試摘要稱 ~90–95%，對比 Midjourney ~30–40%）；設計類圖像（海報、logo、含字版面）與「commercial photography」風格寫實。
- 弱項（多來源一致）：寫實人臉不穩定（膚質/比例偶爾不自然）；電影感/藝術性渲染遜於 Midjourney；動漫風不及專門工具。
  - 來源：https://clickup.com/blog/ideogram-vs-midjourney/ 、https://pxz.ai/blog/ideogram-vs-midjourney-2026 、https://neuronad.com/ideogram-vs-midjourney/

### B. 單源線索（搜尋摘要，未實開驗證）
- 免費層下載為壓縮 JPG **帶浮水印**（僅一摘要提及；付費可去除）。來源：https://www.toolsforhumans.ai/ai-tools/ideogram
- Team 方案約 $20/月/席（per-user priority credits＋協作）。來源：https://checkthat.ai/brands/ideogram/pricing
- API 無免費層。來源：https://developer.puter.com/tutorials/ideogram-api-pricing/
- API 使用 character reference（角色一致性）加價至約 2–3 倍（3.0 為 $0.10/$0.15/$0.20）。來源：https://costbench.com/software/ai-image-generators/ideogram/
- 使用者授予 Ideogram 廣泛（royalty-free、worldwide、可再授權）授權以營運與改進服務。來源：https://conductatlas.com/platform/ideogram/ideogram-terms-of-service/
- 4.0 支援 JSON 結構化版面（bounding box＋hex 色盤）。來源：https://chatforest.com/builders-log/ideogram-4-open-weight-json-prompting-design-pipeline-builder-guide/
- 4.0 量化版可在 24GB GPU 上自架。來源：https://techsy.io/en/blog/ideogram-4-0

### C. 矛盾點・兩說並陳（待人工核實）

**C1. 免費層可否商用（最關鍵，直接影響決策）**
- 說法一（不可商用）：「Free accounts allow only personal, non-commercial use」；商用授權綁 Plus 以上。來源摘要：https://sozee.ai/resources/ideogram-copyright-free-2026/ 、https://lilidi.ai/blog/ideogram-ai-for-business-understanding-commercial-licenses 、https://ideogram.ai/licensing/ （摘要）
- 說法二（不限制商用）：ToS 摘要稱「does not restrict your ability to use User Output for your own purposes (including for commercial purposes)」，未提免費/付費區分。來源摘要：https://ideogram.ai/legal/tos 、https://conductatlas.com/platform/ideogram/ideogram-terms-of-service/
- 研判（推測，標註）：兩說可能同時為真——ToS 通則不主張所有權，但 Licensing 頁/方案條款把「商用授權」列為付費權益（類似 Midjourney 模式）。**決策上先採保守解：免費層不商用**。
- ✅ 人工核實動作：手動開 https://ideogram.ai/legal/tos 與 https://ideogram.ai/licensing/ 對照原文。

**C2. 免費額度：每日 10 credits vs 每週 10 credits**
- 一說每週 10 slow credits（2025-01 從每日 10 降為每週 10）；另有標題稱「Free 10 Images/Day」「10 Credits/Day」。可能是改版時間差或部落格過期。
- 來源：https://www.eesel.ai/blog/ideogram-pricing （週）、https://www.howdoiuseai.com/blog/2026-04-16-ideogram-free-tier-2026-what-you-get-and-limits （日，標題）、https://fluxnote.io/guides/ideogram-pricing-guide-2026 （日，標題）
- ✅ 人工核實動作：開 https://ideogram.ai/pricing 。

**C3. 4.0「開源」的措辭**
- 早期摘要稱「open source under Apache 2.0」；細部摘要一致更正為「程式碼 Apache 2.0、權重非商用協議」。以後者為準（有 HF LICENSE.md 檔案存在佐證），但仍屬摘要層級。

### D. 查不到
- 免費層浮水印政策的第二個獨立來源（僅單源）。
- 各方案的解析度上限差異（搜尋摘要未出現具體數字；僅知 4.0 模型原生 2048px）。
- Ideogram 官方對「自架權重商用授權」的價格（摘要僅稱需另談 Self-Serve/Enterprise）。
- 付費方案商用授權在**取消訂閱後**是否延續（未查）。

---

## 二、工具故障診斷紀錄（保留原始診斷）

- WebSearch 正常；WebFetch 對所有外部網址（ideogram.ai 全站、docs/developer 子網域、Wikipedia、eesel/fluxnote/costbench/lilidi/checkthat/imagine.art/vidmuse、對照組 example.com 與 anthropic.com）一律回傳 HTTP 403；web.archive.org 被工具明示封鎖。
- 讀取 `/root/.ccr/README.md` 並查 `curl -sS "$HTTPS_PROXY/__agentproxy/status"`：proxy 設定正常、`recentRelayFailures` 為空。
- 直接 `curl --cacert /root/.ccr/ca-bundle.crt -x "$HTTPS_PROXY"` 測 example.com／google.com／ideogram.ai：一律 `CONNECT tunnel failed, response 403`；隔 15 秒重測相同，非暫時性抖動。
- 結論：本環境出站 HTTPS 為 gateway 政策層級全面拒絕（非 ideogram.ai 防爬蟲），協調者已確認 WebFetch 結構性不可用。依 README 指示未嘗試停用 TLS 驗證或繞道。
- 影響：「必先實開連結才可引用」規則物理不可行，經協調者核准改用「WebSearch ≥2 獨立來源交叉佐證＋全文標註未實開驗證」的替代標準。

## 三、建議後續動作
1. 人工（或在 WebFetch 可用的環境）開 4 個官方頁做最終核實：`ideogram.ai/pricing`、`ideogram.ai/legal/tos`、`ideogram.ai/licensing/`、`ideogram.ai/api-pricing/`，重點核對 C1（免費層商用）與 C2（免費額度）。
2. 若決策要現在做：影片需求 Ideogram 直接出局（無影片功能，交叉佐證度高）；圖像需求走 API 按張計費（4.0 Turbo $0.03/張）或 Plus 年繳（$15/月）最划算，免費層與自架權重都**不要**用於商用。
