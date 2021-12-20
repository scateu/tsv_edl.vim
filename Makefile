tsv_edl.tar.gz:
	tar zcvf tsv_edl.tar.gz autoload/ doc/ ftplugin/ ftdetect/ syntax/

deploy:
	rsync --exclude '*.sw?' -av autoload ftdetect ftplugin syntax $(HOME)/.vim

install-utils:
	chmod +x ~/.vim/pack/plugins/start/tsv_edl.vim/utils/tsv2edl.py
	chmod +x ~/.vim/pack/plugins/start/tsv_edl.vim/utils/srt2tsv_all.py
	chmod +x ~/.vim/pack/plugins/start/tsv_edl.vim/utils/tsv2srt.py
	chmod +x ~/.vim/pack/plugins/start/tsv_edl.vim/utils/tsv2srt_all.py
	chmod +x ~/.vim/pack/plugins/start/tsv_edl.vim/utils/audio2srtvideo.sh
	ln -s ~/.vim/pack/plugins/start/tsv_edl.vim/utils/tsv2edl.py /usr/local/bin/tsv2edl
	ln -s ~/.vim/pack/plugins/start/tsv_edl.vim/utils/srt2tsv_all.py /usr/local/bin/srt2tsv_all
	ln -s ~/.vim/pack/plugins/start/tsv_edl.vim/utils/audio2srtvideo.sh /usr/local/bin/audio2srtvideo
	ln -s ~/.vim/pack/plugins/start/tsv_edl.vim/utils/tsv2srt.py /usr/local/bin/tsv2srt
	ln -s ~/.vim/pack/plugins/start/tsv_edl.vim/utils/tsv2srt_all.py /usr/local/bin/tsv2srt_all
uninstall-utils:
	rm /usr/local/bin/tsv2edl
	rm /usr/local/bin/srt2tsv_all
	rm /usr/local/bin/audio2srtvideo
	rm /usr/local/bin/tsv2srt
	rm /usr/local/bin/tsv2srt_py

install-ffmpeg-mac: ffplay-4.4.1.7z ffmpeg-4.4.1.7z
	for f in $^; do 7z e ./$$f; done
	mv ffmpeg ffplay utils/
	chmod +x utils/ffplay
	chmod +x utils/ffmpeg
	ln -s $(PWD)/utils/ffmpeg /usr/local/bin/ffmpeg
	ln -s $(PWD)/utils/ffplay /usr/local/bin/ffplay
	rm -i $^

ffplay-4.4.1.7z ffmpeg-4.4.1.7z:
	wget https://evermeet.cx/ffmpeg/$@
