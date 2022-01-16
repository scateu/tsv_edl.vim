file_a="${1%.*}_a.txt"
file_b="${1%.*}_b.txt"
file_c="${1%.*}_c.txt"
file_d="${1%.*}_d.txt"
file_en_zh="${1%.*}_en_zh.srt"
file_zh="${1%.*}_zh.srt"


cat "${1}" |grep '^EDL' > "${file_a}" #full line
cat "${1}" |grep '^EDL' | sed -E 's/.*\|\t(.*)$/\1/' > "${file_b}" #col 5
cat "${1}" |grep '^EDL' | sed -E 's/(.*\|\t).*$/\1/' > "${file_d}"  #col 1,2,3,4

if [[ -f "${file_c}" ]]; then
	echo "${file_c} found. concatenating "
	paste "${file_a}" "${file_c}"  | sed 's/\t/\\N/5' | tsv2srt > "${file_en_zh}"
	paste "${file_d}" "${file_c}"  | grep -v '\[ 空间 .* 秒' | sed 's/\t//4' |  tsv2srt > "${file_zh}"
	echo "${file_en_zh} and ${file_zh} generated."
	rm -i "${file_a}" "${file_b}" "${file_d}"
	rm -i "${file_c}" 
else
	echo "now translate '${file_b}' by hand to '${file_c}'"
	echo "and run again"
fi
