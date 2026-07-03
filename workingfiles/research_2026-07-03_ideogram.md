# Ideogram 商用圖像／影片生成調查（2026-07-03）

## 結論（一句話）
**任務失敗（工具卡點）**：WebSearch 可正常運作並找到多個線索，但 WebFetch（含整個 proxy 出站連線）在本次 session 完全失效（對 ideogram.ai、Wikipedia、google.com、anthropic.com、example.com 全部回傳 403），導致無法依規定「實際開啟來源頁面讀過才引用」，因此**無法產出符合驗收條件的已驗證報告**。以下只列出 WebSearch 摘要（明確標示為未驗證線索）與工具故障的診斷紀錄，禁止把未驗證內容當作確認事實使用。

---

## 一、方法與工具狀態

### 已嘗試的操作
1. `WebSearch`：正常運作，執行了 5 組查詢（Ideogram pricing、最新版本、video generation、ToS 商用條款、API pricing）。
2. `WebFetch`：對以下所有網址皆回傳 `HTTP 403 Forbidden`，無一成功：
   - `https://ideogram.ai/pricing`
   - `https://docs.ideogram.ai/plans-and-pricing/available-plans`
   - `https://ideogram.ai/legal/tos`
   - `https://ideogram.ai/licensing/`
   - `https://docs.ideogram.ai/frequently-asked-questions`
   - `https://ideogram.ai/features/api-pricing`
   - `https://ideogram.ai`、`https://docs.ideogram.ai`、`https://developer.ideogram.ai`
   - `https://web.archive.org/...`（工具回報「Claude Code is unable to fetch from web.archive.org」）
   - `https://www.eesel.ai/blog/ideogram-pricing`
   - `https://fluxnote.io/guides/ideogram-pricing-guide-2026`
   - `https://costbench.com/software/ai-image-generators/ideogram/`
   - `https://lilidi.ai/blog/ideogram-ai-for-business-understanding-commercial-licenses`
   - `https://en.wikipedia.org/wiki/Ideogram_(text-to-image_model)`
   - `https://checkthat.ai/brands/ideogram/pricing`
   - `https://www.imagine.art/blogs/ideogram-4-0-overview`
   - `https://vidmuse.ai/blog/ideogram-4-0`
   - **對照組（排除是否為 ideogram.ai 網站專屬封鎖）**：`https://example.com`、`https://www.anthropic.com` 也同樣回傳 403。

### 診斷過程（排除「這是 ideogram.ai 專屬防爬蟲」的可能性）
- 讀取 `/root/.ccr/README.md`，並執行 `curl -sS "$HTTPS_PROXY/__agentproxy/status"`：`recentRelayFailures` 為空，代理設定本身（CA、port、noProxy）看起來正常。
- 直接用 `curl --cacert /root/.ccr/ca-bundle.crt -x "$HTTPS_PROXY"` 測試 `https://example.com`、`https://www.google.com`、`https://ideogram.ai/pricing`，三者皆回傳同樣的錯誤：`curl: (56) CONNECT tunnel failed, response 403`。
- 間隔 15 秒後重測 `example.com`，結果相同（非暫時性抖動）。
- 結論：**這不是 ideogram.ai 的機器人防護單獨擋掉本工具，而是本次 session 的出站 HTTPS（WebFetch 與底層 proxy CONNECT）整體被拒絕（403）**，屬於環境/工具層級故障，而非可透過調整網址、User-Agent、或改用封存站繞過的問題。依 `/root/.ccr/README.md` 指示，「403 from the proxy」屬於「do not retry or route around it — report the blocked host」的類別，已如實回報，未嘗試停用 TLS 驗證或繞過代理。

### 結果
- 沒有任何一個來源被「實際開啟讀取」，包含 ideogram.ai 官方頁面、Wikipedia、以及各媒體/部落格頁面。
- 依使用者規定的方法要求：「只出現在搜尋清單、未實開的連結禁止引用」，以下第二節內容**一律不得當作確認事實使用**，僅供使用者知悉 WebSearch 摘要線索、待工具恢復後再驗證。

---

## 二、WebSearch 摘要線索（未經 WebFetch 驗證，僅供參考，不可視為確認事實）

> 以下段落全部來自 WebSearch 回傳的搜尋引擎摘要文字，**未經開啟原始頁面核實**，可能有過期、錯誤、或 AI 摘要幻覺風險。使用者若要據此做「用不用 Ideogram」的決策，建議工具恢復後重新查證，或請使用者自行手動開啟下列網址核對。

### 1. 最新模型版本
- 搜尋摘要指出：Ideogram 3.0 於 2025 年 3 月發布；Ideogram 4.0 於 2026 年 6 月 3 日發布，號稱是 Ideogram 首個開放權重（open-weight）文生圖模型，採 Apache 2.0 授權，93 億參數 Diffusion Transformer。
- 來源（未驗證）：https://ideogram.ai/models/3.0/ 、https://www.imagine.art/blogs/ideogram-4-0-overview 、https://en.wikipedia.org/wiki/Ideogram_(text-to-image_model)

### 2. 免費方案
- 摘要指出：免費方案每週約 10 個「slow credits」；另有摘要稱免費帳號僅供個人非商用（non-commercial），且產出預設公開（public）。
- **注意：兩則搜尋摘要對「免費方案是否可商用」的說法互相矛盾**——其中一則摘要（疑似混雜了付費方案條款）稱「Ideogram does not claim any ownership... does not restrict commercial use」，另一則明確稱「Free accounts allow only personal, non-commercial use」。這正是本任務要求「查 ToS 原文」的原因，但因 WebFetch 失效，**無法開啟 https://ideogram.ai/legal/tos 或 https://ideogram.ai/licensing/ 核實哪個說法正確，也無法確認免費層浮水印政策**。
- 來源（未驗證）：https://fluxnote.io/guides/ideogram-pricing-guide-2026 、https://docs.ideogram.ai/plans-and-pricing/available-plans 、https://ideogram.ai/legal/tos 、https://ideogram.ai/licensing/

### 3. 付費方案
- 摘要指出：Plus 方案年繳約 $15/月起，Pro 方案最高約 $42/月（年繳可省 25%~30%），另有 Team 方案約 $20/月/席。差異據稱包含私人生成（private generation）、更快的優先佇列、更多額度。**確切級距、額度數字、解析度差異未經核實**。
- 來源（未驗證）：https://ideogram.ai/pricing 、https://checkthat.ai/brands/ideogram/pricing

### 4. API 定價
- 摘要指出每張圖片價格區間（未核實）：
  - Ideogram 4.0：Turbo $0.03、Default $0.06、Quality $0.10
  - Ideogram 3.0：Turbo/Default/Quality 約 $0.03/$0.06/$0.09
  - Ideogram 2a Turbo：$0.025；Ideogram 1.0 Turbo：$0.02
  - 使用角色參考圖（character reference）費用另計，據稱漲至 2–3 倍。
- 來源（未驗證）：https://ideogram.ai/features/api-pricing 、https://developer.puter.com/tutorials/ideogram-api-pricing/ 、https://costbench.com/software/ai-image-generators/ideogram/

### 5. 商用授權關鍵條款
- 摘要聲稱付費方案下 Ideogram 不主張 User Output 的所有權，使用者可商用（但需遵守協力廠商權利與 Acceptable Use Policy，且不可用產出訓練競品模型）。免費方案是否適用同一條款**有矛盾說法，未核實**（見上第 2 點）。
- 來源（未驗證）：https://ideogram.ai/legal/tos 、https://ideogram.ai/licensing/ 、https://lilidi.ai/blog/ideogram-ai-for-business-understanding-commercial-licenses

### 6. 影片生成能力
- 多則摘要一致指出：**Ideogram（含 4.0）本身沒有原生影片生成功能**，只做靜態圖像；使用者需搭配 Pika、Runway、Filmora 等外部工具把圖片轉成影片（例如 Ken Burns 效果）。此點多來源說法一致，方向上可信度較高，但仍建議之後用 WebFetch 開啟官方頁面（如 https://ideogram.ai/ 首頁）二次確認「目前」是否仍無影片功能。
- 來源（未驗證）：https://fluxnote.io/guides/how-to-turn-ideogram-image-into-video 、https://vidmuse.ai/blog/ideogram-4-0

### 7. 強項與弱項
- 摘要指出 Ideogram 的強項是圖內文字渲染準確率高（摘要稱約 90%，對比 Midjourney 約 30%，此數字未核實、疑似行銷或部落格誇飾），以及 3.0/4.0 版本強調寫實度（skin tone、光線物理、反射）與設計風格一致性（Style Reference）。弱項未在搜尋摘要中明確提及，**查不到**。

---

## 三、依必查清單逐項狀態

| # | 項目 | 狀態 |
|---|------|------|
| 1 | 最新版本與定位（是否有 4.0） | 查不到（WebSearch 摘要稱有 4.0，2026-06-03發布，但未經 WebFetch 核實官方頁面） |
| 2 | 免費方案額度／商用／公開／浮水印 | 查不到（來源互相矛盾，且無法開啟 ToS/pricing 原文核實） |
| 3 | 付費方案價格與差異 | 查不到（僅有未核實搜尋摘要數字） |
| 4 | API 定價 | 查不到（僅有未核實搜尋摘要數字） |
| 5 | 商用授權關鍵條款 | 查不到（無法開啟 ideogram.ai/legal/tos、ideogram.ai/licensing/ 原文） |
| 6 | 影片生成能力 | 查不到（但多則獨立摘要方向一致：目前無原生影片生成，需搭配外部工具；建議工具恢復後仍需二次確認） |
| 7 | 強項弱項 | 查不到（僅查到強項摘要：文字渲染、寫實、風格一致性；弱項未查到） |

已查過的地方：ideogram.ai 官方 pricing/ToS/licensing/FAQ/API pricing 頁、docs.ideogram.ai、developer.ideogram.ai、Wikipedia、web.archive.org、以及 eesel.ai、fluxnote.io、costbench.com、lilidi.ai、checkthat.ai、imagine.art、vidmuse.ai 等部落格/媒體頁 —— **全部因 WebFetch/proxy 403 故障而無法實際開啟**。

---

## 四、建議後續動作
1. 這是本次 session 的環境/代理層故障（出站 HTTPS 全面 403），不是 ideogram.ai 網站的防爬蟲問題。建議稍後（換一個 session 或環境恢復後）重新執行本任務，屆時應可用 WebFetch 開啟：
   - `https://ideogram.ai/pricing`（訂閱方案與額度）
   - `https://ideogram.ai/legal/tos` 與 `https://ideogram.ai/licensing/`（商用授權原文，特別是免費層是否可商用的矛盾說法）
   - `https://ideogram.ai/features/api-pricing`（API 單價）
   - `https://ideogram.ai/`（確認是否仍無影片生成功能）
2. 若使用者急需初步方向判斷（不作為最終商用決策依據）：多個獨立來源方向一致地指出 Ideogram 目前（含 4.0）**沒有原生影片生成功能**，這點置信度相對較高；但「免費方案能否商用」出現矛盾說法，**在核實 ToS 原文前，建議先假設免費層不可商用**，以策安全。
