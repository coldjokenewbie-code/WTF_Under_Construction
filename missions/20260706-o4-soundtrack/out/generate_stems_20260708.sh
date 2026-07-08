#!/usr/bin/env bash
# O4 配樂重做（路線C×方向二）：呼叫 Vertex AI lyria-002 生成 6 段素材 raw wav。
# 前提：使用者已在 MISSION 討論閘拍板「方向二」（見 ../_blockers.md）。
# 已查證（music-research_2026-07-08.md 事實1，來源=Google 官方 lyria2 notebook）：
#   端點 .../publishers/google/models/lyria-002:predict；固定輸出 30s/48kHz wav；
#   request 參數 = prompt（必填）/ negative_prompt（選填）/ sample_count（選填）/ seed（選填，不可與 sample_count 同用）。
# 未查證（notebook 未列出，本次網路白名單也無法開官方 API 參考頁核對，見 music-research 開放問題1）：
#   回傳 JSON 欄位名稱。本檔採用 Vertex 其他生成媒體 API（Imagen 等）常見慣例
#   `predictions[].bytesBase64Encoded`；若實測不符，請印出 raw JSON（腳本已保留 .response.json）核對正確欄位再改 python 解碼段。
#
# Prompt 全文與畫面錨點見同目錄 prompts_route-C_direction2_20260708.md；本檔僅放 API 呼叫用的精簡版。
set -euo pipefail

: "${GCP_PROJECT:?請填 GCP project id}"
: "${GCP_LOCATION:?請填 Vertex AI 服務所在 region，例如 us-central1（未查證是否為 Lyria 可用區域，請自行核對）}"

OUT_DIR="${OUT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/raw}"
mkdir -p "${OUT_DIR}"

echo "== 檢查 gcloud Application Default Credentials =="
if ! command -v gcloud >/dev/null 2>&1; then
  echo "錯誤: 找不到 gcloud CLI，請先安裝並執行 gcloud init。" >&2
  exit 1
fi
if ! gcloud auth application-default print-access-token >/dev/null 2>&1; then
  echo "錯誤: 尚未設定 Application Default Credentials，請先執行: gcloud auth application-default login" >&2
  exit 1
fi
ACCESS_TOKEN="$(gcloud auth application-default print-access-token)"
ENDPOINT="https://${GCP_LOCATION}-aiplatform.googleapis.com/v1/projects/${GCP_PROJECT}/locations/${GCP_LOCATION}/publishers/google/models/lyria-002:predict"
echo "ADC 驗證通過。project=${GCP_PROJECT} location=${GCP_LOCATION}"

declare -A PROMPTS
declare -A NEG_PROMPTS

PROMPTS[opening_S1]="Solo low piano single-note pulse, uneven and irregular timing, not a steady grid, like an unsteady heartbeat losing its rhythm, minor key, pulse mostly sparse and hesitant at first then a low sustained drone gradually thickens beneath it, occasional faint minor-second dissonant shadow tone, dark and unresolved mood, restrained institutional documentary underscore, no melody, no vocals, piano pulse and drone are the only elements present, sits very low in the mix beneath narration, 30 seconds"
NEG_PROMPTS[opening_S1]="vocals, singing, lead melody, orchestral swell, cinematic trailer hit, upbeat pop, drum kit, percussion loop, saxophone, guitar"

PROMPTS[opening_S2]="Low piano single-note pulse that has now locked into a steady, even, confident grid, institution taking shape, tonal center brightening from minor to major, low drone continues but calmer and steadier beneath, moderate density, orderly and settling mood, restrained institutional documentary underscore, no melody, no vocals, piano pulse is the only rhythmic element present, sits very low in the mix beneath narration, 30 seconds"
NEG_PROMPTS[opening_S2]="${NEG_PROMPTS[opening_S1]}"

PROMPTS[opening_S3]="Steady low piano pulse continues in major key, a warm mid-frequency string pad enters gently beneath and around it adding local homely warmth, briefly for about one second the pulse stumbles out of time before immediately recovering back to steady, a fleeting shadow not a full return to instability, restrained institutional documentary underscore, no melody, no vocals, piano pulse remains the only rhythmic element present, sits very low in the mix beneath narration, 30 seconds"
NEG_PROMPTS[opening_S3]="vocals, singing, lead melody, orchestral swell, cinematic trailer hit, upbeat pop, drum kit, percussion loop, saxophone, guitar, traditional Chinese instrument timbre"

PROMPTS[opening_S4]="Low piano pulse gradually dissolves and slows into a single long sustained tone, string pad and low drone fade together with it, ending on a calm bright quietly resolved sustained chord that trails toward near silence, restrained institutional documentary underscore, no melody, no vocals, tranquil and settled, 30 seconds"
NEG_PROMPTS[opening_S4]="vocals, singing, lead melody, orchestral swell, cinematic trailer hit, upbeat pop, drum kit, percussion loop"

PROMPTS[event1985_E1]="Solo low piano single-note pulse, the same steady institutional heartbeat motif as the main title theme, extremely minimal and thin in the mix, mostly restrained with a faint low drone underneath, staying out of the way of a busy foreground, no melody, no vocals, piano pulse is the only rhythmic element present, major key, calm and neutral, sits very low in the mix, 30 seconds"
NEG_PROMPTS[event1985_E1]="${NEG_PROMPTS[opening_S1]}"

PROMPTS[event1985_E2]="Low piano pulse from the same motif settles into an even steadier warmer statement, a warm string pad joins gently beneath it, gradually the pulse dissolves into a single sustained tone that trails toward near silence at the very end, restrained institutional documentary underscore, no melody, no vocals, major key, warm and quietly resolved, 30 seconds"
NEG_PROMPTS[event1985_E2]="${NEG_PROMPTS[opening_S1]}"

for KEY in opening_S1 opening_S2 opening_S3 opening_S4 event1985_E1 event1985_E2; do
  RESPONSE_FILE="${OUT_DIR}/${KEY}.response.json"
  WAV_FILE="${OUT_DIR}/${KEY}.wav"
  echo "== 生成 ${KEY} =="

  REQUEST_BODY=$(python3 - "${PROMPTS[$KEY]}" "${NEG_PROMPTS[$KEY]}" <<'PYEOF'
import json, sys
prompt, neg = sys.argv[1], sys.argv[2]
print(json.dumps({
  "instances": [{"prompt": prompt, "negative_prompt": neg}],
  "parameters": {"sample_count": 1}
}))
PYEOF
)

  curl -sS -X POST \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json; charset=utf-8" \
    "${ENDPOINT}" \
    -d "${REQUEST_BODY}" \
    -o "${RESPONSE_FILE}"

  python3 - "${RESPONSE_FILE}" "${WAV_FILE}" <<'PYEOF'
import base64, json, sys
resp_path, wav_path = sys.argv[1], sys.argv[2]
with open(resp_path) as f:
    data = json.load(f)
if "error" in data:
    print(f"錯誤回應（見 {resp_path}）：{data['error']}", file=sys.stderr)
    sys.exit(1)
try:
    b64 = data["predictions"][0]["bytesBase64Encoded"]
except (KeyError, IndexError):
    print(f"欄位不符預期，請開 {resp_path} 核對正確欄位名稱後手動解碼。", file=sys.stderr)
    sys.exit(1)
with open(wav_path, "wb") as f:
    f.write(base64.b64decode(b64))
print(f"已寫入 {wav_path}")
PYEOF
done

cat <<'EOF'

== 6 段素材生成完畢 ==
下一步：跑 assemble_v4_20260708.sh 把 raw/ 內的 wav 依接合點裁切+crossfade，
輸出 Opening_v4.mp3（66.3s）與 Event1985_v4.mp3（40.0s）。
EOF
