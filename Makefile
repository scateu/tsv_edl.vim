DIR := ${CURDIR}

tsv_edl.tar.gz:
	tar zcvf tsv_edl.tar.gz autoload/ doc/ ftplugin/ ftdetect/ syntax/

deploy:
	rsync --exclude '*.sw?' -av autoload ftdetect ftplugin syntax $(HOME)/.vim

install-utils:
	chmod +x ${CURDIR}/utils/tsv2edl.py
	chmod +x ${CURDIR}/utils/srt2tsv_all.py
	chmod +x ${CURDIR}/utils/tsv2srt.py
	chmod +x ${CURDIR}/utils/tsv2srt_all.py
	chmod +x ${CURDIR}/utils/audio2srtvideo.sh
	chmod +x ${CURDIR}/utils/audio2video.sh
	chmod +x ${CURDIR}/utils/tsv2roughcut.py
	chmod +x ${CURDIR}/utils/mkgap_10_mp3
	chmod +x ${CURDIR}/utils/mkgap_10_mp4
	chmod +x ${CURDIR}/utils/tsv2srt_reflow.py
	chmod +x ${CURDIR}/utils/srt2tsv.sh
	chmod +x ${CURDIR}/utils/scenecut_preview.sh
	chmod +x ${CURDIR}/utils/audiocut.sh
	chmod +x ${CURDIR}/utils/srt2txt.sh
	chmod +x ${CURDIR}/utils/tsv2zh_cn.sh
	chmod +x ${CURDIR}/utils/tsv2fcpxml.py
	sudo ln -sf ${CURDIR}/utils/tsv2edl.py /usr/local/bin/tsv2edl
	sudo ln -sf ${CURDIR}/utils/srt2tsv_all.py /usr/local/bin/srt2tsv_all
	sudo ln -sf ${CURDIR}/utils/audio2srtvideo.sh /usr/local/bin/audio2srtvideo
	sudo ln -sf ${CURDIR}/utils/audio2video /usr/local/bin/audio2video
	sudo ln -sf ${CURDIR}/utils/tsv2srt.py /usr/local/bin/tsv2srt
	sudo ln -sf ${CURDIR}/utils/tsv2srt_all.py /usr/local/bin/tsv2srt_all
	sudo ln -sf ${CURDIR}/utils/tsv2roughcut.py /usr/local/bin/tsv2roughcut
	sudo ln -sf ${CURDIR}/utils/mkgap_10_mp4 /usr/local/bin/mkgap_10_mp4
	sudo ln -sf ${CURDIR}/utils/mkgap_10_mp3 /usr/local/bin/mkgap_10_mp3
	sudo ln -sf ${CURDIR}/utils/tsv2srt_reflow.py /usr/local/bin/tsv2srt_reflow
	sudo ln -sf ${CURDIR}/utils/srt2tsv.sh /usr/local/bin/srt2tsv
	sudo ln -sf ${CURDIR}/utils/scenecut_preview.sh /usr/local/bin/scenecut_preview
	sudo ln -sf ${CURDIR}/utils/audiocut.sh /usr/local/bin/audiocut
	sudo ln -sf ${CURDIR}/utils/srt2txt.sh /usr/local/bin/srt2txt
	sudo ln -sf ${CURDIR}/utils/tsv2zh_cn.sh /usr/local/bin/tsv2zh_cn
	sudo ln -sf ${CURDIR}/utils/tsv2fcpxml.py /usr/local/bin/tsv2fcpxml

uninstall-utils:
	cd /usr/local/bin; sudo rm -i audio2video audio2srtvideo mkgap_10_mp3 mkgap_10_mp4 srt2tsv srt2tsv_all tsv2edl tsv2roughcut tsv2srt tsv2srt_all tsv2srt_reflow scenecut_preview srt2txt tsv2zh_cn audiocut

install-depends-on-mac-no-homebrew: install-ffmpeg-mac install-jq-mac install-mpv-mac install-socat-mac
	rm -i ffmpeg-mac.zip mpv-latest.tar.gz socat_macOS.bin jq_macOS.bin

fetch-mac: ffmpeg-mac.zip mpv-latest.tar.gz jq_macOS.bin socat_macOS.bin

install-ffmpeg-mac: ffmpeg-mac.zip
	unzip ffmpeg-mac.zip
	chmod +x ffmpeg
	sudo mv ffmpeg /usr/local/bin/

install-mpv-mac: mpv-latest.tar.gz
	tar zxvf mpv-latest.tar.gz
	mv mpv.app /Applications/
	rm -r documentation/
	sudo ln -sf /Applications/mpv.app/Contents/MacOS/mpv /usr/local/bin/mpv

install-jq-mac: jq_macOS.bin
	chmod +x $<
	sudo cp $< /usr/local/bin/jq

install-socat-mac: socat_macOS.bin
	chmod +x socat_macOS.bin
	sudo cp socat_macOS.bin /usr/local/bin/socat

jq_macOS.bin:
	curl -JL https://github.com/stedolan/jq/releases/download/jq-1.6/jq-osx-amd64 -o jq_macOS.bin

ffmpeg-mac.zip:
	curl -JL https://evermeet.cx/ffmpeg/getrelease/zip -o $@


mpv-latest.tar.gz:
	curl -JL https://laboratory.stolendata.net/~djinn/mpv_osx/mpv-latest.tar.gz -o $@

socat_macOS.bin:
	curl -JL https://github.com/3ndG4me/socat/releases/download/v1.7.3.3/socat_macOS.bin -o $@
