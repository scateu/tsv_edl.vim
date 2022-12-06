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

## VIDEO (if you insist)

 - see: <https://github.com/termux/termux-x11>
 - see: <https://www.youtube.com/watch?v=lB9eqixqSS8>

in `.termux/termux.properties`, uncomment this line:

	allow-external-apps = true

Install some packages:

	$ pkg install ./termux-x11.deb 
	$ xdg-open app-debug.apk   #install this apk

	$ pkg install x11-repo mpv-x
	$ vi $PREFIX/etc/apt/sources.list.d/x11.list
	deb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-x11 x11 main

	$ export XDG_RUNTIME_DIR=${TMPDIR}
	$ termux-x11 :1 &
	$ export DISPLAY=:1 

	$ echo "vo=x11" >> $PREFIX/etc/mpv/mpv.conf
	$ find ./ -name *.vim -exec sed -i 's,mpv --,mpv -vo=x11 --,g' {} \;
	
Some patient may be needed after press `\\`.

Some commands:
	$ mpv -vo=x11 ./video.mp4
	Press 'f' to go fullscreen, to avoid only a portion of video is displayed.
	# https://github.com/termux/termux-packages/issues/5057


## TIPS: ssh into termux

	$ passwd
	$ sshd

from outside:

	$ ssh -p8022 <username>@IP-OF-Android


## TIPS: mpv in text terminal

	mpv --vo=tct ./video.mp4
