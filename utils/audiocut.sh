#!/bin/bash

media="$1"
threshold=-50 #dB
duration=4  #sec

last_start="NA"
last_stop="NA"

handle_args() {
#secs2timecode() {
	local start
	local stop
	local duration
	while read start stop duration; do
		if [[ "$last_start" != "NA" ]]; then
			printf "EDL\t${last_start}\t${last_stop}\t| ${media%.*} |\tSOMEONE SAID SOMETHING\n"
		fi
		printf "EDL\t"
		line=$start
		h=$(bc <<< "$line/3600")
		m=$(bc <<< "($line%3600)/60")
		s=$(bc <<< "$line%60")
		last_start=$(printf "%02d:%02d:%06.3f" $h $m $s)
		printf "$last_start\t"
		line=$stop
		h=$(bc <<< "$line/3600")
		m=$(bc <<< "($line%3600)/60")
		s=$(bc <<< "$line%60")
		last_stop=$(printf "%02d:%02d:%06.3f" $h $m $s)
		printf "$last_stop\t"
		printf "| ${media%.*} |\t"
		printf "[ SPACE ${duration} secs ] \n"
	done
}

echo "Writing to ${media%.*}_audiocut.tsv"

echo "Silence detect threshold: ${threshold} dB"
echo "Silence detect duration: ${duration} sec"

ffmpeg -y -i "./${media}" -af "silencedetect=n=${threshold}dB:d=${duration}" -f null - 2>&1 | sed -n -E -l '/silence_start/p; /silence_end/p;' | sed -n -E -l '/silence_start/ {s/^.*silence_start: //; N; s/\n.*silence_end:/ /; s/\|.*silence_duration: //; p;}' | handle_args | tee "${media%.*}_audiocut.tsv"


#|  sed -n -E -l '/^.*showinfo.*pts_time.*$/ {s/.*pts_time:([0-9]+\.?[0-9]+).*/\1/g;p;}'  |  secs2timecode |  sed -n -l 'N;s/\./,/g;h;s/\n/	/;p;x;D;' | sed -l 's/^/EDL	/' | sed -l "s/$/	| ${media%.*} |	/" | tee 