## 装xcode command tools

    xcode-select --install

安装 Xcode 命令行工具。


tips: Homebrew卸载

	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)”


mac command line tools离线安装

	https://developer.apple.com/download/all/
	https://mac.install.guide/commandlinetools/6.html

## 装homebrew

https://brew.idayer.com/

安装:

    /bin/bash -c "$(curl -fsSL https://gitee.com/ineo6/homebrew-install/raw/master/install.sh)"

记得再做一遍:

    export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
    export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.ustc.edu.cn/homebrew-core.git"
    export HOMEBREW_API_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/api"
    export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/bottles"


## 装依赖

    mkdir -p ~/.vim/pack/plugins/start; cd ~/.vim/pack/plugins/start
    git clone https://gh.idayer.com/https://github.com/scateu/tsv_edl.vim
    git clone https://gh.idayer.com/https://github.com/vim-airline/vim-airline
    git clone https://gh.idayer.com/https://github.com/pR0Ps/molokai-dark
    make install-utils
    brew install ffmpeg mpv socat jq dos2unix yt-dlp 

## macvim 去网站上下载dmg好了

<https://macvim.org/>


如果用homebrew来装

	brew install --cask macvim

略慢
