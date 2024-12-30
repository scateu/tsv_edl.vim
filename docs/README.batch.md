# Batch add overley and credit

For example, for vertical influencers, 

1. Change all 1920 1080 accordingly in `tsv2roughcut.py`
2. something like this `do.sh`

```bash
#!/bin/bash

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

shopt -s nullglob

for i in *.mp4 *.MP4
    do 
	    echo $i
	    duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $i | secs2timecode | sed 's/\./,/g')
	    echo $duration
	    cat TEMPLATE.tsv | sed "s/TIMECODE/${duration}/g" | sed "s/FILENAME/${i%%.*}/"
	    cat TEMPLATE.tsv | sed "s/TIMECODE/${duration}/g" | sed "s/FILENAME/${i%%.*}/" | python3 tsv2roughcut.py
	    mv roughcut.mp4 rCut_${i%%.*}.mp4
	    rm roughcut.srt 
    done
```


TEMPLATE.tsv:

```
EDL	00:00:00,000	TIMECODE	| overlay |	[B] Overlay
EDL	00:00:00,000	TIMECODE	| FILENAME |	Main Video
EDL	00:00:00,000	00:00:02,000	| something1 |	Credit 1
EDL	00:00:00,000	00:00:02,000	| something2 |	Credit 2
```
