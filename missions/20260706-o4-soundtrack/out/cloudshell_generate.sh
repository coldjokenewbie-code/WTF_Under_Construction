#!/bin/bash
# 存保影片四開場配樂:一鍵生成(在 Google Cloud Shell 貼上執行)
# 依據:配樂設計書 v2(文案 v2_20260707,時間碼 5/15/13/12/15s)
# 產出:A_影片四開場_60s.wav / B_影片四開場_60s.wav(48kHz,10 段 lyria-002 生成+裁剪+0.15s 淡接)
# 費用:20 次 lyria-002 生成(計費)。約 5-10 分鐘。
set -euo pipefail
PROJECT=$(gcloud config get-value project 2>/dev/null)
echo "專案:$PROJECT;開始生成(lyria-002, us-central1)…"

python3 - "$PROJECT" << 'PYEOF'
import json, sys, base64, subprocess, urllib.request, wave, struct, array, os, time

PROJECT = sys.argv[1]
URL = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/us-central1/publishers/google/models/lyria-002:predict"

# ============ v2 段落與 prompts(單一真相源) ============
# (時長秒, prompt)
A = [  # 方案A:檔案室的燈|D小調→F大調|60 BPM|celesta+弦樂四重奏+單簧管
 (5,  "Solo celesta only, a clear three-note motif descending then ascending then descending, 60 BPM, D minor, very sparse single instrument, long cathedral reverb, pianissimo, intimate archival museum mood, no vocals, no drums, no strings"),
 (15, "Neutral sustained string quartet long tones with a calm solo clarinet line, 60 BPM, D minor, even and unemotional, documentary neutrality, chamber music, thin texture, no melody drama, no vocals, no drums, no piano"),
 (13, "Chamber string quartet, low cello shadow line with soft pizzicato bass pulses and a hint of minor-second tension resolving into an ordered clarinet melody with gentle rhythmic order, D minor moving toward F major, 60 BPM, 1930s documentary gravity, no vocals, no drums"),
 (12, "String quartet with a subtle pentatonic-inflected viola and violin line woven into determined steady chamber rhythm, growing warmth and resolve, F major, 60 BPM, East Asian hint without any traditional instruments, no erhu, no guzheng, no vocals, no drums"),
 (15, "Warm full string quartet with celesta returning on a three-note motif, broad open F major full cadence, settled and reassuring conclusion, museum documentary warmth, gentle decay to silence at the end, 60 BPM, no vocals, no drums"),
]
B = [  # 方案B:制度的脈搏|C小調→C大調|66 BPM|鋼琴脈衝+弦樂pad+低頻drone
 (5,  "Single repeated soft piano note pulse like a calm heartbeat, 66 BPM, C minor, completely minimal, dry intimate room, no other instruments, no vocals, no drums"),
 (15, "Minimal steady soft piano pulse at even intervals with a very quiet sustained string pad underneath, 66 BPM, C minor, neutral institutional calm, no melody, no vocals, no drums"),
 (13, "Slowing sparse piano pulse over a deepening low drone, tension of scarcity, then the pulse regains strict regular order with a second interlocking piano voice, C minor, 66 BPM, minimalist, no vocals, no drums"),
 (12, "Two interlocking minimal piano pulse voices with rising density and a warm mid-range string pad joining, quiet determination, C minor brightening, 66 BPM, minimalist process music, no vocals, no drums"),
 (15, "Minimal piano pulse relaxing into a slow secure heartbeat over a warm C major string pad, brightening resolution, settled and safe, gradually fading to silence, 66 BPM, no vocals, no drums"),
]
SEGS = {"A": A, "B": B}
FADE = 0.15   # 段界淡入淡出秒數
TAIL = 0.5    # 末段結尾靜默秒數(含在最後一段時長內)

def token():
    return subprocess.run(["gcloud","auth","print-access-token"],capture_output=True,text=True,check=True).stdout.strip()

def gen(prompt, retries=2):
    body = json.dumps({"instances":[{"prompt":prompt}],"parameters":{"sample_count":1}}).encode()
    for i in range(retries+1):
        try:
            req = urllib.request.Request(URL, data=body, headers={"Authorization":"Bearer "+token(),"Content-Type":"application/json"})
            r = urllib.request.urlopen(req, timeout=300)
            p = json.loads(r.read())["predictions"][0]
            b64 = p.get("audioContent") or p.get("bytesBase64Encoded")
            if not b64: raise RuntimeError("回應無音訊欄位:"+str(list(p.keys())))
            return base64.b64decode(b64)
        except Exception as e:
            if i == retries: raise
            print(f"  重試({e})…"); time.sleep(8)

def read_wav(b):
    open("/tmp/_seg.wav","wb").write(b)
    w = wave.open("/tmp/_seg.wav","rb")
    par = w.getparams(); frames = w.readframes(par.nframes); w.close()
    assert par.sampwidth == 2, f"非16bit PCM:{par.sampwidth}"
    return par, array.array("h", frames)

def build(case, segs):
    out = array.array("h"); par0 = None
    for n,(dur,prompt) in enumerate(segs,1):
        print(f"[{case} 段{n}/{len(segs)}] {dur}s 生成中…")
        par, pcm = read_wav(gen(prompt))
        if par0 is None: par0 = par
        assert (par.framerate,par.nchannels)==(par0.framerate,par0.nchannels), "段間格式不一致"
        ch, sr = par.nchannels, par.framerate
        need = int(dur*sr)*ch
        seg = pcm[:need]
        if len(seg) < need: seg.extend([0]*(need-len(seg)))
        f = int(FADE*sr)*ch
        for i in range(f):     # 淡入
            seg[i] = int(seg[i]*(i/f))
        for i in range(f):     # 淡出
            j = len(seg)-1-i; seg[j] = int(seg[j]*(i/f))
        if n == len(segs):     # 末段:尾部強制靜默 TAIL 秒
            t = int(TAIL*sr)*ch
            for i in range(len(seg)-t, len(seg)): seg[i] = 0
        out.extend(seg)
    name = f"{case}_影片四開場_60s.wav"
    w = wave.open(name,"wb"); w.setnchannels(par0.nchannels); w.setsampwidth(2)
    w.setframerate(par0.framerate); w.writeframes(out.tobytes()); w.close()
    print(f"→ {name}:{len(out)/par0.nchannels/par0.framerate:.2f}s, {par0.framerate}Hz")

for case, segs in SEGS.items():
    build(case, segs)
print("完成。驗收表見 配樂設計書 v2;下載:Cloud Shell 右上「⋮」→ Download,或 cloudshell download A_影片四開場_60s.wav")
PYEOF

echo "=== TTS 佔位配音(Cloud TTS cmn-TW)==="
gcloud services enable texttospeech.googleapis.com --quiet 2>/dev/null || true
python3 - << 'TTSEOF'
import json, base64, subprocess, urllib.request
def token():
    return subprocess.run(["gcloud","auth","print-access-token"],capture_output=True,text=True,check=True).stdout.strip()
TEXTS = {
 "opening_vo": "銀行因「以短支長」的經營模式，較會面臨流動性風險與擠兌威脅。存款保險制度旨在穩定民眾信心，但為防範經營者的道德風險，必須搭配嚴謹的金融監理。回顧歷史，1929年，美國經濟大蕭條導致近萬家銀行倒閉，美國政府為此成立全球首創的聯邦存款保險公司，成為臺灣制度的參考基石。民國70年代，臺灣隨金融自由化風險增加，加上美國伊利諾州大陸銀行危機的國際震撼，促使國內加速推動存保立法。如今，臺灣每人在同一機構最高享有新臺幣300萬元保障，有效化解了過去銀行倒閉、存款可能會損失的歷史夢魘。",
 "e1_vo": "1985年，台北市第十信用合作社爆發嚴重違規超貸，引發民眾擠兌衝擊金融信心。政府意識到臺灣迫切需要一套存款保障機制，參照美國存保制度設計，正式成立中央存款保險公司。初期採自由投保、單一費率，每位存款人最高保額新臺幣七十萬元，我國的金融安全網從此正式扎根。"
}
for name, text in TEXTS.items():
    body = json.dumps({
      "input":{"text":text},
      "voice":{"languageCode":"cmn-TW","name":"cmn-TW-Wavenet-B"},
      "audioConfig":{"audioEncoding":"LINEAR16","speakingRate":0.94,"pitch":-1.5,"sampleRateHertz":44100}
    }).encode()
    req = urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize",
        data=body, headers={"Authorization":"Bearer "+token(),"Content-Type":"application/json"})
    d = json.loads(urllib.request.urlopen(req, timeout=120).read())
    open(name+".wav","wb").write(base64.b64decode(d["audioContent"]))
    print(name+".wav OK")
TTSEOF

echo "=== 推回 repo(音樂+配音一次入庫)==="
[ -d claude_CDIC_O4 ] || git clone -q https://github.com/coldjokenewbie-code/claude_CDIC_O4.git
mkdir -p claude_CDIC_O4/public/audio/music claude_CDIC_O4/public/audio/vo
cp A_影片四開場_60s.wav B_影片四開場_60s.wav claude_CDIC_O4/public/audio/music/
cp opening_vo.wav e1_vo.wav claude_CDIC_O4/public/audio/vo/
cd claude_CDIC_O4 && git add public/audio && git commit -m "配樂A/B(lyria)+TTS佔位配音(Cloud TTS) [CloudShell]" && git push
echo "全部完成——回 Claude session 說「音檔已推」即可。"
