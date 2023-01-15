#!/bin/bash

# without srt

audio="$1"
#srt="${audio%.*}.srt"

ffmpeg -f lavfi -i "color=#172F47:s=800x450" \
	-i "$audio"  \
	-filter_complex "drawtext=fontcolor=white:boxcolor=#172F47:text='${audio%.*}':x=(w-text_w)/2:y=(h-text_h)*0.1:box=1:boxborderw=2:fontsize=30,\
	drawtext=font=monospace:x=(w-text_w)/2:y=(h-text_h)*0.55:fontcolor=white:boxcolor=black:box=1:boxborderw=2:text='TC\: %{pts\:hms}':fontsize=14" \
	-r 24 \
       	-shortest \
	"${audio%.*}.mkv"

# timecode drawtext ref: https://stackoverflow.com/questions/3169916/can-ffmpeg-burn-in-time-code

# for debug: -t 10 \
