#!/usr/bin/env bash
# 未查證: Lyria model id 與端點,執行前先查官方文件
#   （本 stub 的 Vertex AI 端點路徑、request body 欄位名、回傳格式皆未實測過，
#    請先 `gcloud ai models list` 或查 Vertex AI 官方文件確認後再修改 TODO 區塊。）
#
# 用途: 依 `配樂設計書.md` 的方案 A/B 各五段時間碼，逐段呼叫 Vertex AI 音樂生成
# 佔位端點，產出 wav 檔供人工剪接與對齊驗收。Prompt 全文見同目錄 prompts.md，
# 本檔內僅放置各段 Lyria prompt 供 API request body 直接引用。
#
# 正本以 `配樂設計書.md` 為準，本檔任何段落文字如與設計書衝突，以設計書為準。

set -euo pipefail

# ---------------------------------------------------------------------------
# 0. 必填環境變數（不編造預設值，缺一律報錯中止）
# ---------------------------------------------------------------------------
: "${LYRIA_MODEL:?請填 Vertex AI 上的 Lyria model id/資源名稱，例如
  publishers/google/models/<未查證-請自行確認>；勿照抄，先查官方文件}"
: "${GCP_PROJECT:?請填 GCP project id}"
: "${GCP_LOCATION:?請填 Vertex AI 服務所在 region，例如 us-central1（未查證是否為正確 region，請自行確認 Lyria 可用區域）}"

OUT_DIR="${OUT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

# ---------------------------------------------------------------------------
# 1. gcloud ADC 檢查
# ---------------------------------------------------------------------------
echo "== 檢查 gcloud Application Default Credentials =="

if ! command -v gcloud >/dev/null 2>&1; then
  echo "錯誤: 找不到 gcloud CLI，請先安裝並執行 gcloud init。" >&2
  exit 1
fi

if ! gcloud auth application-default print-access-token >/dev/null 2>&1; then
  echo "錯誤: 尚未設定 Application Default Credentials。" >&2
  echo "請先執行: gcloud auth application-default login" >&2
  exit 1
fi

ACCESS_TOKEN="$(gcloud auth application-default print-access-token)"
echo "ADC 驗證通過。project=${GCP_PROJECT} location=${GCP_LOCATION} model=${LYRIA_MODEL}"

# ---------------------------------------------------------------------------
# 2. 各段時間碼（照設計書：0-5 / 5-20 / 20-35 / 35-50 / 50-60）
# ---------------------------------------------------------------------------
SEG_STARTS=(0 5 20 35 50)
SEG_ENDS=(5 20 35 50 60)

# 每段 Lyria prompt（英文，完整版見 prompts.md；此處為 API 呼叫直接引用版本）
declare -A PROMPTS

PROMPTS[A_1]="Solo celesta, three-note motif descending-ascending-descending, 60 BPM, D minor, very sparse, long cathedral reverb, pianissimo, archival intimate mood, no vocals, no drums, museum documentary, 6 seconds with natural decay tail"
PROMPTS[A_2]="String quartet, celesta motif handed off to low strings pizzicato, cello long sustained bowed shadow line with minor-second friction dissonance, 60 BPM, D minor, gradually increasing density from sparse to moderate, uneasy restrained mood, not sentimental, archival documentary, very low-level vinyl surface noise beneath -40dB, no vocals, no drums, 16 seconds with natural decay tail"
PROMPTS[A_3]="Clarinet takes over the celesta motif as lead melody, string quartet with viola countermelody, tonal center shifting toward F major, 60 BPM, a felt pulse emerging through phrasing (institution being born, order forming), moderate density, warmer and more settled mood than prior section, archival documentary, very low-level vinyl surface noise beneath -40dB, no vocals, no drums, 16 seconds with natural decay tail"
PROMPTS[A_4]="String quartet with clarinet and celesta color, a pentatonic-flavored melodic fragment woven subtly into the string line (evoke Taiwan without literal traditional Chinese instrument timbre -- no erhu, no guzheng, no pipa), F major, 60 BPM, mezzo-forte, rising warmth, moderate-full density, archival documentary, very low-level vinyl surface noise beneath -40dB, no vocals, no drums, 16 seconds with natural decay tail"
PROMPTS[A_5]="Main celesta motif returns in unison with full string quartet, crescendo, D minor to F major tonal ambiguity resolving into a suspended half cadence (history left unresolved, not a final resolution), ending sustained on an open fifth interval, 60 BPM, archival documentary, grand but restrained, no vocals, no drums, 11 seconds total, ending in 0.5 second of trailing silence for UI handoff (10 seconds material + natural decay/silence tail)"

PROMPTS[B_1]="Solo piano single-note pulse, steady and even like a secure heartbeat, 66 BPM, C minor, no melody, extremely minimal, no other instruments, restrained institutional mood, no vocals, piano pulse is the only rhythmic element present (do not remove or mute the pulse), 6 seconds with natural decay tail"
PROMPTS[B_2]="Piano single-note pulse with intervals gradually lengthening and sparser, low sustained drone entering beneath, 66 BPM grid but felt as slowing/sluggish, C minor, sparse density, stagnant and depressed mood (depression era heartbeat slowing), restrained institutional tone, no vocals, no other percussion beyond the piano pulse, 16 seconds with natural decay tail"
PROMPTS[B_3]="Second piano voice locks into sync with the original pulse (institution taking shape), tonal center flips brighter from C minor to C major exactly at this section, 66 BPM, moderate density, low drone continues beneath, cautiously settling and more orderly mood, restrained institutional tone, no vocals, no other percussion beyond the piano pulses, 16 seconds with natural decay tail"
PROMPTS[B_4]="Warm mid-frequency string pad joins beneath the locked-in piano pulses, C major, 66 BPM, moderate-full density, low drone still present, warmth rising, settled and reassuring mood, restrained institutional tone, no vocals, no other percussion beyond the piano pulses, 16 seconds with natural decay tail"
PROMPTS[B_5]="Piano pulse splits into echoing fragments that gradually fade out, string pad and low drone fade with it, ending sustained on an open fifth interval (same cadence device as Plan A), C major, 66 BPM, restrained institutional tone, no vocals, no other percussion beyond the piano pulse echoes, 11 seconds total, ending in 0.5 second of trailing silence for UI handoff (10 seconds material + natural decay/silence tail)"

# TODO(未查證): 確認正確的 Vertex AI 端點路徑；下方為佔位變數，勿照跑。
VERTEX_ENDPOINT="https://${GCP_LOCATION}-aiplatform.googleapis.com/v1/projects/${GCP_PROJECT}/locations/${GCP_LOCATION}/publishers/google/models/${LYRIA_MODEL}:predict"

# ---------------------------------------------------------------------------
# 3. 迴圈 10 段（A/B × 5），呼叫 Vertex 端點佔位變數
# ---------------------------------------------------------------------------
for CASE in A B; do
  for i in "${!SEG_STARTS[@]}"; do
    SEG_NO=$((i + 1))
    START="${SEG_STARTS[$i]}"
    END="${SEG_ENDS[$i]}"
    KEY="${CASE}_${SEG_NO}"
    PROMPT="${PROMPTS[$KEY]}"
    OUT_FILE="${OUT_DIR}/${CASE}_seg${SEG_NO}_${START}-${END}.wav"

    echo "== 生成 ${KEY}: ${START}-${END}s -> $(basename "${OUT_FILE}") =="

    # TODO(未查證): request body 欄位名（prompt/duration/sampleCount 等）
    # 未經 Vertex AI 官方文件核實，以下為佔位示意，勿直接照跑。
    REQUEST_BODY=$(cat <<JSON
{
  "instances": [
    {
      "prompt": $(printf '%s' "${PROMPT}" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
    }
  ],
  "parameters": {
    "sampleCount": 1
  }
}
JSON
)

    # TODO(未查證): curl 呼叫本身（headers、回傳是否為 base64 音訊等）皆未實測。
    curl -sS -X POST \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json; charset=utf-8" \
      "${VERTEX_ENDPOINT}" \
      -d "${REQUEST_BODY}" \
      -o "${OUT_FILE}.response.json" || {
        echo "警告: ${KEY} 呼叫失敗，略過（此為未驗證 stub，請先確認端點與參數）" >&2
        continue
      }

    # TODO(未查證): 從回傳 JSON 解出音訊並寫成 wav 的實際欄位路徑未知，
    # 以下僅為示意 placeholder，不保證可執行。
    echo "已寫入回應: ${OUT_FILE}.response.json（尚未轉出 ${OUT_FILE}，請依官方文件補上音訊解碼步驟）"
  done
done

# ---------------------------------------------------------------------------
# 4. 收尾提示：跑設計書的對齊驗收表
# ---------------------------------------------------------------------------
cat <<'EOF'

== 全部段落生成完畢（或已略過失敗段） ==

下一步，請對照 `配樂設計書.md` 的「對齊驗收表」逐項確認：
  - [ ] 各段轉場落點 5.0/20.0/35.0/50.0（±0.5s，對 PRD 畫面結構）
  - [ ] 全長 60.0s 含尾 0.5s 靜默；-18 LUFS；無爆音（true peak ≤ -1dBTP）
  - [ ] 主動機在 0–5 與 50–60 兩段可辨識（系列識別成立）
  - [ ] 五聲音階段不含具體國樂器音色（檢查 35–50）
  - [ ] 業主試聽二選一後，依 anchors/README 把落選案+理由寫入 anchors/配樂.md 首批錨點

提醒：本 stub 的 Vertex AI 端點路徑與回傳格式皆未查證，
生成失敗或格式不符時，請先查 Vertex AI Lyria 官方文件再修正腳本，不要盲目重跑。
EOF
