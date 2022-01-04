clipname="${1%.*}"
mediainfo $1 |grep ": CHAPTER" | sed -n    's/\./,/;N;h;s/\n/\t/;p;x;D;' | awk -v OFS='\t' '{print "EDL",$1,$4,'"\"| ${clipname} |\""',$3}'

