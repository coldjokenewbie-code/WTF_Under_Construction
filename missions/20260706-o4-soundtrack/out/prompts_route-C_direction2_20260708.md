# O4 配樂生成 Prompts — 路線 C × 方向二「制度的脈搏」

> 依據：`配樂定調書_2026-07-08.md` 第三、五節（Opening 66.3s 五幕表、Event1985 40s 簡表）與第七節路線收斂（方向二×路線C＝次選但唯一可行 fallback，見 `_blockers.md`：lyria-002=400可用、lyria-3*=404）。
> 正本以定調書為準，本檔任何段落文字如與定調書衝突，以定調書為準。
> **點頭前禁生成音檔**——本檔只是「拍板後可直接跑」的備料，寫 prompt/腳本本身不算生成音檔。

## 設計原則（為何切成這幾段，不是照畫面幕數切）

lyria-002 每次呼叫固定輸出 **30 秒**、無 continuation/extend 參數（`music-research_2026-07-08.md` 事實1）。方向二的核心是「單一鋼琴脈衝動機的狀態演變」，所以**不能**指望一次生成內部自己從「不穩」變到「鎖定」——那是兩次不同 prompt 生成的素材，靠後製 crossfade 接合才會產生「演變」的聽感。因此段落切法＝「每段素材對應動機的一個穩定狀態」，接合點對齊畫面轉場，而不是每個畫面幕各自生成一段。

每段素材生成時長固定 30s，實際用量（餵給 `acrossfade` 的長度）小於等於 30s，多出的部分裁掉。裁切長度已按 crossfade 重疊量反推，使接合點準確落在畫面轉場秒數（見下方每段的「用量」與 `assemble_v4_20260708.sh` 的算式）。

## Opening（66.3s，接合點 26.0s／48.6s／60.5s，crossfade=1.5s）

### S1｜用量 26.75s（覆蓋 0–3.6 開門 + 3.6–26 崩塌）
```
prompt: Solo low piano single-note pulse, uneven and irregular timing, not a steady grid, like an unsteady heartbeat losing its rhythm, minor key, pulse mostly sparse and hesitant at first then a low sustained drone gradually thickens beneath it, occasional faint minor-second dissonant shadow tone, dark and unresolved mood, restrained institutional documentary underscore, no melody, no vocals, piano pulse and drone are the only elements present, sits very low in the mix beneath narration, 30 seconds
negative_prompt: vocals, singing, lead melody, orchestral swell, cinematic trailer hit, upbeat pop, drum kit, percussion loop, saxophone, guitar
```
畫面錨點：13.6–17.5s「1929 大蕭條」＝全片最暗點，此段素材需能撐住這個情緒重量（陰影/半音摩擦音）。

### S2｜用量 24.10s（覆蓋 26–48.6 秩序的建立）
```
prompt: Low piano single-note pulse that has now locked into a steady, even, confident grid, institution taking shape, tonal center brightening from minor to major, low drone continues but calmer and steadier beneath, moderate density, orderly and settling mood, restrained institutional documentary underscore, no melody, no vocals, piano pulse is the only rhythmic element present, sits very low in the mix beneath narration, 30 seconds
negative_prompt: vocals, singing, lead melody, orchestral swell, cinematic trailer hit, upbeat pop, drum kit, percussion loop, saxophone, guitar
```
畫面錨點：26s＝脈衝第一次「鎖定」規律；39.4s FDIC＝第一個明亮和聲。

### S3｜用量 13.40s（覆蓋 48.6–60.5 台灣的回聲）
```
prompt: Steady low piano pulse continues in major key, a warm mid-frequency string pad enters gently beneath and around it adding local homely warmth, briefly for about one second the pulse stumbles out of time before immediately recovering back to steady, a fleeting shadow not a full return to instability, restrained institutional documentary underscore, no melody, no vocals, piano pulse remains the only rhythmic element present, sits very low in the mix beneath narration, 30 seconds
negative_prompt: vocals, singing, lead melody, orchestral swell, cinematic trailer hit, upbeat pop, drum kit, percussion loop, saxophone, guitar, traditional Chinese instrument timbre
```
畫面錨點：53.8–60.7s 伊利諾大陸銀行段＝短暫失拍/陰影一筆即收（禁具體國樂器音色，沿定調書題材鐵律）。

### S4｜用量 6.55s（覆蓋 60.5–66.3 抵達）
```
prompt: Low piano pulse gradually dissolves and slows into a single long sustained tone, string pad and low drone fade together with it, ending on a calm bright quietly resolved sustained chord that trails toward near silence, restrained institutional documentary underscore, no melody, no vocals, tranquil and settled, 30 seconds
negative_prompt: vocals, singing, lead melody, orchestral swell, cinematic trailer hit, upbeat pop, drum kit, percussion loop
```
畫面錨點：65.3s 黑幕起 decay 至無聲。

## Event1985（40.0s，接合點 23.25s，crossfade=2.0s；同一家族動機，非獨立寫一首）

### E1｜用量 24.25s（覆蓋 0–21.6 滿版事件影片，音樂極薄）
```
prompt: Solo low piano single-note pulse, the same steady institutional heartbeat motif as the main title theme, extremely minimal and thin in the mix, mostly restrained with a faint low drone underneath, staying out of the way of a busy foreground, no melody, no vocals, piano pulse is the only rhythmic element present, major key, calm and neutral, sits very low in the mix, 30 seconds
negative_prompt: vocals, singing, lead melody, orchestral swell, cinematic trailer hit, upbeat pop, drum kit, percussion loop, saxophone, guitar
```

### E2｜用量 17.75s（覆蓋 21.6–40.0 三張定像，脈衝轉穩＋暖收）
```
prompt: Low piano pulse from the same motif settles into an even steadier warmer statement, a warm string pad joins gently beneath it, gradually the pulse dissolves into a single sustained tone that trails toward near silence at the very end, restrained institutional documentary underscore, no melody, no vocals, major key, warm and quietly resolved, 30 seconds
negative_prompt: vocals, singing, lead melody, orchestral swell, cinematic trailer hit, upbeat pop, drum kit, percussion loop, saxophone, guitar
```

## 接合點反推算式（供覆核，公式見 `assemble_v4_20260708.sh` 註解）

設 n 段素材用量 U₁..Uₙ、crossfade 長度 CF，第 k 個接合點（畫面轉場秒數）＝ `Σ(U₁..Uₖ) − (k−0.5)×CF`；全長 ＝ `ΣUᵢ − (n−1)×CF`。

Opening（CF=1.5）：U=[26.75, 24.10, 13.40, 6.55] → 接合點 26.0 / 48.6 / 60.5，全長 66.3 ✓
Event1985（CF=2.0）：U=[24.25, 17.75] → 接合點 23.25（落在畫面轉場窗 21.6–24.9 內），全長 40.0 ✓
