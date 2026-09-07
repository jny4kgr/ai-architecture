#!/bin/zsh
# 連番PNG (render/anim/<shot>/f_####.png) → ショットごとの mp4 → 0.5秒クロスフェードで結合
# 使い方: ./make_video.sh   (出力: render/roomtour_20s.mp4)
set -e
cd "$(dirname "$0")"
FPS=24
XF=0.5
SUFFIX=${SUFFIX:-}
OUT=render/roomtour_20s${SUFFIX}.mp4
ANIM=render/anim${SUFFIX}
shots=(01_外観一周 02_1F車庫 03_1F玄関 04_2F_LDK 05_3F_洋室A)

inputs=()
durs=()
for s in $shots; do
  ffmpeg -y -loglevel error -framerate $FPS -i "$ANIM/$s/f_%04d.png" \
    -c:v libx264 -pix_fmt yuv420p -crf 18 "$ANIM/$s.mp4"
  n=$(ls $ANIM/$s/f_*.png | wc -l | tr -d ' ')
  durs+=($(echo "scale=3; $n / $FPS" | bc))
  inputs+=(-i "$ANIM/$s.mp4")
done

# xfade チェーン: offset は累積尺 - フェード分
filter=""
prev="[0:v]"
offset=0
for ((i=1; i<${#shots[@]}; i++)); do
  offset=$(echo "scale=3; $offset + ${durs[$i]} - $XF" | bc)
  out="[v$i]"
  filter+="${prev}[$i:v]xfade=transition=fade:duration=$XF:offset=$offset$out;"
  prev=$out
done
filter=${filter%;}

ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "$filter" -map "$prev" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart "$OUT"
echo "WROTE $OUT"; ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
