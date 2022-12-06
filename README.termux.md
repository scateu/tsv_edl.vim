# INSTALLATION on Termux

Install [termux](https://mirrors.tuna.tsinghua.edu.cn/help/termux/) from [fdroid](https://mirrors.tuna.tsinghua.edu.cn/help/fdroid/), Google Play version is deprecated.

(optional)

	$ termux-change-repo
	$ vi $PREFIX/etc/apt/sources.list.d/x11.list
	deb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-x11 x11 main
 
Install packages:

	pkg install vim jq socat make git
	pkg install x11-repo mpv-x

Patch some:

	$ cd ~/.vim/pack/plugins/start/tsv_edl.vim/
	$ find ./ -name *.vim -exec sed -i 's,/tmp/mpvsocket,~/mpvsocket,g' {} \;
	$ sed -i 's,/usr/local/bin/,/data/data/com.termux/files/usr/bin/,g' Makefile
	$ make install-utils


## TIPS: ssh into termux

	$ passwd
	$ sshd

from outside:

	$ ssh -p8022 <username>@IP-OF-Android
