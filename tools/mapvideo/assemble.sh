#!/usr/bin/env bash
# Join rendered scene files with the voice track. Run in the work folder after the story script.
# Usage: bash assemble.sh <output.mp4>
set -euo pipefail
OUT="${1:?output file}"
ls scenes/c*.mp4 | grep -v tmp | sort | sed "s#^#file '$PWD/#; s#\$#'#" > scenes/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i scenes/list.txt -c copy scenes/_video.mp4
ffmpeg -y -loglevel error -i scenes/_video.mp4 -i audio/voice.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "${OUT%.mp4}.tmp.mp4"
mv "${OUT%.mp4}.tmp.mp4" "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
