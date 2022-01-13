#!/bin/bash

media="$1"
preview="${media%.*}_preview.png"

secs2timecode() {
	local line
	while read line; do
		h=$(bc <<< "$line/3600")
		m=$(bc <<< "($line%3600)/60")
		s=$(bc <<< "$line%60")
		printf "%02d:%02d:%06.3f\n" $h $m $s
		#| sed 's/\./,/' >> /tmp/b
	done
}

echo "writing to ${media}_scenecut.tsv"
ffmpeg -y -i "./${media}" -vf "select=gt(scene\,0.4),showinfo,scale=160:-1,tile=6x80" -frames:v 1 -qscale:v 3 "${preview}" 2>&1 |  sed -n -r -l '/^.*showinfo.*pts_time.*$/ {s/.*pts_time:([0-9]+\.?[0-9]+).*/\1/g;p;}'  |  secs2timecode |  sed -n -l 'N;s/\./,/g;h;s/\n/\t/;p;x;D;' | sed -l 's/^/EDL\t/' | sed -l "s/$/\t| ${media%.*} |\t/" | tee "${media%.*}_scenecut.tsv"

#|  dc -e '?1~r60~r60~r[[0]P]szn[:]ndZ2>zn[:]ndZ2>zn[[.]n]sad0=ap' | 

# https://blog.gdeltproject.org/using-ffmpegs-scene-detection-to-generate-a-visual-shot-summary-of-television-news/
# https://stackoverflow.com/questions/12199631/convert-seconds-to-hours-minutes-seconds

#ffmpeg -f lavfi -i "movie=${media},scdet=s=1:t=14" -vf "scale=160:-1,tile=6x85" -frames:v 1 -qscale:v 3 "${preview}"

