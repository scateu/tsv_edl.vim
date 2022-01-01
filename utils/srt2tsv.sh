#!/bin/bash


HEADER="EDL\tRecord In\tRecord Out\tClipname\tSubtitle"

function convert_it () {
	echo -e ${HEADER}
	sed -n -r '1{/^$/n;};/^[0-9]+$/{n; s/ --> /\t/; s/$/\t| _CLIPNAME_ |/; h; d;}; /^$/! {H; $!d;}; x; s/\n/\t/g; s/^/EDL\t/;p'

	# '1{/^$/n;}; #第一行可能有空行
	# /^[0-9]+$/{ # 起始行
           # n;
	   # s/ --> /\t/; 
	   # s/$/\t| _CLIPNAME_ |/; 
	   # h; 
	   # d;
        # }; 
	# /^$/! { #非空
	   #   H; $!d;  #Hold一行
        # };
	# # 余下所有
	# x; s/\n/\t/g; s/^/EDL\t/;p'
	# }
}

if [ $# -eq 1 ]; then
	basename="${1%.*}"
	cat "$1" | convert_it | sed "s/_CLIPNAME_/${basename}/" > "${1%.*}.tsv"
	echo "${1%.*}.tsv written."
fi

if [ $# -eq 0 ]; then
	convert_it
fi
