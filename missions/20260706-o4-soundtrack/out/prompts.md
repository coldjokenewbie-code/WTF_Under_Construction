# 存保 O 區影片 4 配樂生成 Prompts

> 正本:`配樂設計書.md`。本檔不得偏離其配器/BPM/調性/時間碼/禁忌;如有疑義以設計書為準。
> 段時長規則:每段 Lyria prompt 標註「實際秒數 + 1s decay tail」。
> 例外:方案 B 的脈衝(piano pulse)是節奏骨幹本身,非鼓組——B 案五段皆不寫「no drums」,僅寫「no vocals」,避免生成模型把脈衝也濾掉;A 案五段照設計書維持「no vocals, no drums」。

---

## 方案 A「檔案室的燈」(懷舊敘事型)

配器與理由(照設計書,全五段共用):弦樂四重奏(避免大編制罐頭,保留呼吸與私密感)、鋼片琴 celesta(檔案的微光,替代鋼琴)、單簧管(1930 年代木質空氣)、極低量類黑膠底噪(-40dB 以下,年代顆粒)。主動機:celesta 三音「下—上—下」。基調 D 小調→F 大調,60 BPM 全程恆定。

### A 段 1 | 0.0–5.0s | 畫面:標題淡入,深背景

**Lyria prompt:**
```
Solo celesta, three-note motif descending-ascending-descending, 60 BPM, D minor,
very sparse, long cathedral reverb, pianissimo, archival intimate mood,
no vocals, no drums, museum documentary, 6 seconds with natural decay tail
```

**工具中立文字版:**
獨奏鋼片琴彈奏「下—上—下」三音主動機,60 BPM、D 小調,極稀疏、長殘響、極弱音,不鋪任何底,莊重留白的檔案室氛圍。
無人聲、無鼓組;時長 6 秒(5 秒實際+1 秒自然衰減尾音)。

---

### A 段 2 | 5.0–20.0s | 畫面:美國大蕭條 Ken Burns

**Lyria prompt:**
```
String quartet, celesta motif handed off to low strings pizzicato,
cello long sustained bowed shadow line with minor-second friction dissonance,
60 BPM, D minor, gradually increasing density from sparse to moderate,
uneasy restrained mood, not sentimental, archival documentary,
very low-level vinyl surface noise beneath -40dB, no vocals, no drums,
16 seconds with natural decay tail
```

**工具中立文字版:**
主動機轉交低音提琴撥奏,大提琴長弓拉出陰影線與小二度摩擦不協和音,60 BPM、D 小調,密度由稀疏漸增,情緒不安但克制、不煽情,底層極低量黑膠底噪。
無人聲、無鼓組;時長 16 秒(15 秒實際+1 秒自然衰減尾音)。

---

### A 段 3 | 20.0–35.0s | 畫面:FDIC 成立 infographic

**Lyria prompt:**
```
Clarinet takes over the celesta motif as lead melody, string quartet with
viola countermelody, tonal center shifting toward F major, 60 BPM,
a felt pulse emerging through phrasing (institution being born, order forming),
moderate density, warmer and more settled mood than prior section,
archival documentary, very low-level vinyl surface noise beneath -40dB,
no vocals, no drums, 16 seconds with natural decay tail
```

**工具中立文字版:**
單簧管接手主動機成為主旋律,中提琴對位,調性向 F 大調傾斜,60 BPM,樂句本身浮現出有機的節拍感(象徵制度誕生、秩序浮現),情緒轉為安穩。
無人聲、無鼓組;時長 16 秒(15 秒實際+1 秒自然衰減尾音)。

---

### A 段 4 | 35.0–50.0s | 畫面:台灣 1970s

**Lyria prompt:**
```
String quartet with clarinet and celesta color, a pentatonic-flavored melodic
fragment woven subtly into the string line (evoke Taiwan without literal
traditional Chinese instrument timbre — no erhu, no guzheng, no pipa),
F major, 60 BPM, mezzo-forte, rising warmth, moderate-full density,
archival documentary, very low-level vinyl surface noise beneath -40dB,
no vocals, no drums, 16 seconds with natural decay tail
```

**工具中立文字版:**
弦樂四重奏融入五聲音階旋律片段,以暗示台灣意象但不出現具體國樂器音色(不可用二胡/古箏/琵琶),F 大調、60 BPM、中強、溫度上升。
無人聲、無鼓組;時長 16 秒(15 秒實際+1 秒自然衰減尾音)。

---

### A 段 5 | 50.0–60.0s | 畫面:1985 節點亮起

**Lyria prompt:**
```
Main celesta motif returns in unison with full string quartet, crescendo,
D minor to F major tonal ambiguity resolving into a suspended half cadence
(history left unresolved, not a final resolution), ending sustained on an
open fifth interval, 60 BPM, archival documentary, grand but restrained,
no vocals, no drums, 11 seconds total, ending in 0.5 second of trailing
silence for UI handoff (10 seconds material + natural decay/silence tail)
```

**工具中立文字版:**
主動機由 celesta 與弦樂四重奏齊奏回歸並漸強,60 BPM,收在懸而未決的半終止與空五度長音,刻意不完全收束(象徵歷史待續)。
無人聲、無鼓組;時長 11 秒(10 秒實際+1 秒尾音,含收尾前 0.5 秒靜默供金框 UI 接手)。

---

## 方案 B「制度的脈搏」(節制機構型)

配器與理由(照設計書,全五段共用):鋼琴單音脈衝(secure heartbeat)、弦樂長音 pad、低頻 drone。66 BPM 全程恆定(機構的恆常),C 小調→C 大調於 20.0s 明暗翻轉。不寫旋律,靠密度與明暗變化。

### B 段 1 | 0.0–5.0s | 畫面:標題淡入,深背景

**Lyria prompt:**
```
Solo piano single-note pulse, steady and even like a secure heartbeat,
66 BPM, C minor, no melody, extremely minimal, no other instruments,
restrained institutional mood, no vocals, piano pulse is the only rhythmic
element present (do not remove or mute the pulse), 6 seconds with natural
decay tail
```

**工具中立文字版:**
鋼琴以穩定單音脈衝獨奏,如安穩的心跳,66 BPM、C 小調,無旋律、極簡、無其他配器,機構感克制氛圍。
無人聲;脈衝本身即節奏骨幹,不可濾除;時長 6 秒(5 秒實際+1 秒自然衰減尾音)。

---

### B 段 2 | 5.0–20.0s | 畫面:美國大蕭條 Ken Burns

**Lyria prompt:**
```
Piano single-note pulse with intervals gradually lengthening and sparser,
low sustained drone entering beneath, 66 BPM grid but felt as slowing/
sluggish, C minor, sparse density, stagnant and depressed mood
(depression era heartbeat slowing), restrained institutional tone,
no vocals, no other percussion beyond the piano pulse,
16 seconds with natural decay tail
```

**工具中立文字版:**
鋼琴脈衝間隔逐漸拉長變疏,底部加入低頻 drone,66 BPM 但聽感遲滯,C 小調,象徵蕭條期心跳遲緩,情緒低沉克制。
無人聲;除鋼琴脈衝外無其他打擊元素;時長 16 秒(15 秒實際+1 秒自然衰減尾音)。

---

### B 段 3 | 20.0–35.0s | 畫面:FDIC 成立 infographic

**Lyria prompt:**
```
Second piano voice locks into sync with the original pulse (institution
taking shape), tonal center flips brighter from C minor to C major exactly
at this section, 66 BPM, moderate density, low drone continues beneath,
cautiously settling and more orderly mood, restrained institutional tone,
no vocals, no other percussion beyond the piano pulses,
16 seconds with natural decay tail
```

**工具中立文字版:**
第二聲部鋼琴脈衝與主脈衝同步鎖進(制度成形),調性由 C 小調翻轉為 C 大調,66 BPM,情緒轉為謹慎安定、秩序感浮現。
無人聲;除鋼琴脈衝外無其他打擊元素;時長 16 秒(15 秒實際+1 秒自然衰減尾音)。

---

### B 段 4 | 35.0–50.0s | 畫面:台灣 1970s

**Lyria prompt:**
```
Warm mid-frequency string pad joins beneath the locked-in piano pulses,
C major, 66 BPM, moderate-full density, low drone still present,
warmth rising, settled and reassuring mood, restrained institutional tone,
no vocals, no other percussion beyond the piano pulses,
16 seconds with natural decay tail
```

**工具中立文字版:**
在鎖定的鋼琴脈衝底下加入溫暖中頻弦樂 pad,C 大調、66 BPM,密度增加、溫度上升,情緒安定溫暖。
無人聲;除鋼琴脈衝外無其他打擊元素;時長 16 秒(15 秒實際+1 秒自然衰減尾音)。

---

### B 段 5 | 50.0–60.0s | 畫面:1985 節點亮起

**Lyria prompt:**
```
Piano pulse splits into echoing fragments that gradually fade out,
string pad and low drone fade with it, ending sustained on an open fifth
interval (same cadence device as Plan A), C major, 66 BPM,
restrained institutional tone, no vocals, no other percussion beyond the
piano pulse echoes, 11 seconds total, ending in 0.5 second of trailing
silence for UI handoff (10 seconds material + natural decay/silence tail)
```

**工具中立文字版:**
鋼琴脈衝分裂成回聲逐漸淡出,弦樂 pad 與低頻 drone 同步淡出,收在與方案 A 相同的空五度長音,C 大調、66 BPM。
無人聲;時長 11 秒(10 秒實際+1 秒尾音,含收尾前 0.5 秒靜默供金框 UI 接手)。
