# INSTALLATION on Termux

Install [termux](https://mirrors.tuna.tsinghua.edu.cn/help/termux/) from [fdroid](https://mirrors.tuna.tsinghua.edu.cn/help/fdroid/), Google Play version is deprecated.

(optional)

	$ termux-change-repo
 
Install packages:

	$ pkg install vim jq socat make git mpv

Patch some:

	$ cd ~/.vim/pack/plugins/start/tsv_edl.vim/
	$ find ./ -name *.vim -exec sed -i 's,/tmp/mpvsocket,~/mpvsocket,g' {} \;
	$ sed -i 's,/usr/local/bin/,/data/data/com.termux/files/usr/bin/,g' Makefile
	$ make install-utils

The first time you run `mpv` may use some patience. If "[ao/audiotrack] No Java virtual machine has been registered" occurs, stay calm, wait for 20 secs.

## VIDEO (didn't figure out...)

	$ pkg install x11-repo mpv-x
	$ vi $PREFIX/etc/apt/sources.list.d/x11.list
	deb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-x11 x11 main


	export DISPLAY=:1
	mpv -vo=x11 ./video.mp4
	# https://github.com/termux/termux-packages/issues/5057


## TIPS: ssh into termux

	$ passwd
	$ sshd

from outside:

	$ ssh -p8022 <username>@IP-OF-Android


## TIPS: mpv in text terminal

	mpv --vo=tct ./video.mp4
