#!/bin/bash

media="$1"
threshold=0.1
#threshold = 0.1 for webcast
#threshold = 0.4 for movie
#threshold is (0, 1)   the smaller the finer chopped

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

echo "Writing to ${media%.*}_scenecut.tsv"

#ffmpeg -y -i "./${media}" -vf "select=gt(scene\,0.4),showinfo,scale=160:-1,tile=6x80" -frames:v 1 -qscale:v 3 "${preview}" 2>&1 |  sed -n -E -l '/^.*showinfo.*pts_time.*$/ {s/.*pts_time:([0-9]+\.?[0-9]+).*/\1/g;p;}'  |  secs2timecode |  sed -n -l 'N;s/\./,/g;h;s/\n/\t/;p;x;D;' | sed -l 's/^/EDL\t/' | sed -l "s/$/\t| ${media%.*} |\t/" | tee "${media%.*}_scenecut.tsv"
#ffmpeg -y -i "./${media}" -vf "select=gt(scene\,0.1),showinfo" -f null - 2>&1 |  sed -n -E -l '/^.*showinfo.*pts_time.*$/ {s/.*pts_time:([0-9]+\.?[0-9]+).*/\1/g;p;}'  |  secs2timecode |  sed -n -l 'N;s/\./,/g;h;s/\n/\t/;p;x;D;' | sed -l 's/^/EDL\t/' | sed -l "s/$/\t| ${media%.*} |\t/" | tee "${media%.*}_scenecut.tsv"

dirname="${media%.*}_scenecut_images"
mkdir "${dirname}"
echo "Will extract key frames into dir: ${dirname}/"
echo "You may convert * slides.pdf afterwards"
echo "Scene detect threshold: ${threshold}"
#FIXME the first page may be omitted.
ffmpeg -y -i "./${media}" -vf "select=gt(scene\,${threshold}),showinfo"  -vsync vfr "${dirname}/${media%.*}-%05d.png" 2>&1 |  sed -n -E -l '/^.*showinfo.*pts_time.*$/ {s/.*pts_time:([0-9]+\.?[0-9]+).*/\1/g;p;}'  |  secs2timecode |  sed -n -l 'N;s/\./,/g;h;s/\n/	/;p;x;D;' | sed -l 's/^/EDL	/' | sed -l "s/$/	| ${media%.*} |	SCENECUT/" | tee "${media%.*}_scenecut.tsv"
# for lower sed version(2005), \t won't be recognized. Input with C-v <tab>

#|  dc -e '?1~r60~r60~r[[0]P]szn[:]ndZ2>zn[:]ndZ2>zn[[.]n]sad0=ap' | 

# https://blog.gdeltproject.org/using-ffmpegs-scene-detection-to-generate-a-visual-shot-summary-of-television-news/
# https://stackoverflow.com/questions/12199631/convert-seconds-to-hours-minutes-seconds

#ffmpeg -f lavfi -i "movie=${media},scdet=s=1:t=14" -vf "scale=160:-1,tile=6x85" -frames:v 1 -qscale:v 3 "${preview}"

# or 
#FFmpeg Scene selection : extracting iframes and detecting scene change - 2020  ☑
#ffmpeg -i yosemiteA.mp4 -vf "select=gt(scene\,0.5), scale=640:360" -vsync vfr yosemiteThumb%03d.png
#convert *.png -scale 640x360 a.pdf
#cat *.png | ffmpeg -f image2pipe -i - -vf 'scale=128:72,tile=8x8' -an -vsync 0 scene/%03d.png
