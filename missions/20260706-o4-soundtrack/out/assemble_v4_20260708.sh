#!/usr/bin/env bash
# 把 generate_stems_20260708.sh 產出的 raw/*.wav 依「用量+crossfade」裁切接合，
# 輸出 Opening_v4.mp3（66.3s）與 Event1985_v4.mp3（40.0s）。
# 需要 ffmpeg（Mac: brew install ffmpeg）。
#
# 接合點算式（詳見 prompts_route-C_direction2_20260708.md 末節）：
#   第 k 個接合點 = Σ(U1..Uk) − (k−0.5)×CF；全長 = ΣUi − (n−1)×CF
# Opening  CF=1.5  U=[26.75,24.10,13.40,6.55] → 接合點 26.0/48.6/60.5，全長 66.3
# Event1985 CF=2.0 U=[24.25,17.75]           → 接合點 23.25，全長 40.0
set -euo pipefail

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "錯誤：找不到 ffmpeg，請先安裝（Mac: brew install ffmpeg）。" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_DIR="${RAW_DIR:-${SCRIPT_DIR}/raw}"
OUT_DIR="${OUT_DIR:-${SCRIPT_DIR}}"

for f in opening_S1 opening_S2 opening_S3 opening_S4 event1985_E1 event1985_E2; do
  if [ ! -f "${RAW_DIR}/${f}.wav" ]; then
    echo "錯誤：找不到 ${RAW_DIR}/${f}.wav，請先跑 generate_stems_20260708.sh。" >&2
    exit 1
  fi
done

echo "== 組 Opening_v4.mp3（66.3s，接合點 26.0/48.6/60.5） =="
ffmpeg -y \
  -i "${RAW_DIR}/opening_S1.wav" \
  -i "${RAW_DIR}/opening_S2.wav" \
  -i "${RAW_DIR}/opening_S3.wav" \
  -i "${RAW_DIR}/opening_S4.wav" \
  -filter_complex "
    [0:a]atrim=0:26.75,asetpts=PTS-STARTPTS[a0];
    [1:a]atrim=0:24.10,asetpts=PTS-STARTPTS[a1];
    [2:a]atrim=0:13.40,asetpts=PTS-STARTPTS[a2];
    [3:a]atrim=0:6.55,asetpts=PTS-STARTPTS[a3];
    [a0][a1]acrossfade=d=1.5:c1=tri:c2=tri[x1];
    [x1][a2]acrossfade=d=1.5:c1=tri:c2=tri[x2];
    [x2][a3]acrossfade=d=1.5:c1=tri:c2=tri[out]
  " \
  -map "[out]" -ar 48000 -ac 2 -b:a 192k \
  "${OUT_DIR}/Opening_v4.mp3"

echo "== 組 Event1985_v4.mp3（40.0s，接合點 23.25） =="
ffmpeg -y \
  -i "${RAW_DIR}/event1985_E1.wav" \
  -i "${RAW_DIR}/event1985_E2.wav" \
  -filter_complex "
    [0:a]atrim=0:24.25,asetpts=PTS-STARTPTS[a0];
    [1:a]atrim=0:17.75,asetpts=PTS-STARTPTS[a1];
    [a0][a1]acrossfade=d=2.0:c1=tri:c2=tri[out]
  " \
  -map "[out]" -ar 48000 -ac 2 -b:a 192k \
  "${OUT_DIR}/Event1985_v4.mp3"

echo "== 量測實際輸出長度（核對是否為 66.3s / 40.0s，容許 ±0.05s） =="
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${OUT_DIR}/Opening_v4.mp3"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${OUT_DIR}/Event1985_v4.mp3"

cat <<'EOF'

== 完成 ==
下一步（下個 backlog 項，待使用者拍板方向後才做，本次先不動）：
  1. 實聽 Opening_v4.mp3 / Event1985_v4.mp3，對照定調書「對齊驗收表」核對三個接合點聽感、
     1929 陰影段（13.6-17.5s）、FDIC 明亮和聲（39.4s）、結尾收束（65.3s 起）。
  2. 確認後複製到 claude_CDIC_O4 repo：`public/music/Opening_v4.mp3`、`public/music/Event1985_v4.mp3`。
  3. Root.tsx defaultProps 的 music_version 改 4，渲染實播驗收。
EOF
