# 資源登記表（Resource Manifest, SSOT）
> 適用：所有專案、所有 AI agent。需要生成媒體（圖／影片）、去背等能力時先查這裡。
> 來源：WTF_Under_Construction repo。

## 本檔定位（重要）
- 本檔只是**清單(manifest)**：純文字，登記「哪台機器、哪個 OS、有什麼資源、放哪、能不能用」。
- **資源實體（venv、二進位、大檔）一律不放 WTF、不跨機同步。** WTF 是管理中樞，只留清單。
- 資源實體放各機本地（如 `Git_work/gen-tools/`），**各機獨立建置**（`Git_work/` 不同步）。
- **Agent 開場流程**：依「所在機器/OS」查下表 → 判斷本機是否具備該資源 →
  - 有：用登記的路徑。
  - 無但需要：依該資源的「建立方式」建**對應系統版本**，建好後回填本表該機器的路徑/狀態。

## 如何判斷所在機器 / OS
- 機器登錄見 `wtf-config/machines.md`（`sync_config.py register` 自動維護 hostname／OS／workspace_root）。
- OS 由路徑型態判斷：mac=`/Users/...`、windows=`E:\...`（或 `C:\...`）。
- 已登錄機器：`comaMacBookAir`(mac)、`Mac.home`(mac)、`DESKTOP-7SF21LR`(windows, `E:\Git_work\`)。

---

## 資源：Vertex 生圖/影片 腳本（gen-scripts）
- 用途：呼叫 GCP Vertex 生**靜圖**（Imagen／Nano Banana）、**影片**（Veo）。
- 性質：純 Python **stdlib**（urllib + 呼叫 gcloud），**跨平台、無重依賴**。
- 前置（各機各自）：Python3＋gcloud CLI＋跑過一次 `gcloud auth application-default login`。

| 機器 | OS | 路徑 | 狀態 |
|---|---|---|---|
| comaMacBookAir | mac | `/Users/coma/Git_work/gen-tools/` | ✅ 可用 |
| Mac.home | mac | `/Users/coma/Git_work/gen-tools/` | ⬜ 待建（同 mac 步驟） |
| DESKTOP-7SF21LR | windows | `E:\Git_work\gen-tools\` | ⬜ 待建 |

腳本清單：
- `vertex_imagen.py <prompt_file> <out.png> [aspect] [model]`
- `vertex_gemini_image.py <prompt_file> <out.png> [ref_image ...]`（Nano Banana，傳參考圖維持角色一致）
- `vertex_veo.py <prompt_file> <image> <out.mp4> [secs] [aspect] [model]`

建立方式（新機）：把這三支 stdlib 腳本放到該機 `Git_work/gen-tools/`，裝 gcloud CLI，跑一次 ADC login。腳本內 `PROJECT` 用同一計費專案即可（見下）。

---

## 資源：rembg 去背環境（.venv）
- 用途：去背 → 透明 PNG（rembg + onnxruntime）。
- 性質：**系統專用二進位，約 441MB**。`.dylib`/`.so`／`.pyd` 與直譯器路徑綁 OS，**不可跨機/跨平台複用、不同步**。各機必須各自建。

| 機器 | OS | 路徑 | 狀態 |
|---|---|---|---|
| comaMacBookAir | mac | `/Users/coma/Git_work/gen-tools/.venv` | ✅ 可用（Python 3.14.6, rembg 2.0.76） |
| Mac.home | mac | `/Users/coma/Git_work/gen-tools/.venv` | ⬜ 待建 |
| DESKTOP-7SF21LR | windows | `E:\Git_work\gen-tools\.venv` | ⬜ 待建 |

用法（mac，已建）：`/Users/coma/Git_work/gen-tools/.venv/bin/python -c "from rembg import remove; ..."`
建立方式（新機）：`python -m venv <gen-tools>/.venv` 後 `<.venv>/bin/pip install rembg pillow`（Windows 用 `<.venv>\Scripts\pip`）。

---

## GCP Vertex AI — 帳號／計費／模型（帳號級，跨機通用）
> 這段與機器無關：綁 Google 帳號的 ADC，任何機器登入同帳號皆可用。**無需 service account key**。

### 認證
- 取 access token：`gcloud auth application-default print-access-token`（ADC 已登入，scope cloud-platform）。
- 直接以 `Authorization: Bearer <token>` 呼叫 Vertex REST。

### 計費專案
- **`project-c98c8f18-167a-4b0b-968`**（display「My First Project」）：billing 已啟用、`aiplatform.googleapis.com` 已啟用。生圖/影片都用此專案。
- region：Imagen/Veo 用 `us-central1`；Gemini 影像用 `global`。
- 另有兩個 `gen-lang-client-*`（AI Studio/Gemini API）**無 billing**，僅免費層。

### 可用模型與端點
| 用途 | 模型 | 端點 / 方法 | 要點 |
|---|---|---|---|
| 照片級生圖 | `imagen-3.0-generate-002` | `:predict` | 回 base64；param `personGeneration:"allow_adult"`、`aspectRatio`、`addWatermark:false` |
| 角色一致性／參考圖編輯（Nano Banana） | `gemini-2.5-flash-image` | `:generateContent` | `responseModalities:["TEXT","IMAGE"]`；可帶 inlineData 參考圖維持同一人/物 |
| 影片（image-to-video，可含語音） | `veo-3.0-generate-001` | `:predictLongRunning` + `:fetchPredictOperation` 輪詢 | 參數 `durationSeconds`、`aspectRatio`、`generateAudio` |

### 注意事項
- **啟用新 API 會被 Claude Code auto-mode 擋下**（如 `texttospeech.googleapis.com` 尚未啟用），需使用者手動授權或在設定加 Bash 權限規則。
- 生圖提示詞用英文最穩；中文亦可。
- 另有更成熟的 **CSV 批次 + google-genai SDK** 影片生成寫法可參考：`~/Git_work/claude_CDIC_O4/workingfiles/_scripts/`（`veo_generate.py`／`lyria_generate.py`，需 `pip install google-genai`）。
- 首次驗證：2026-06-17 於本機成功用 Imagen 生人物 hero、Nano Banana 帶參考圖生一致對嘴來源幀。
