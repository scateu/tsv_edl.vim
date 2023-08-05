# run on neovim

macOS:
 - install VimR

 - install Plug

```bash
sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs \
       https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'

```

```
$ cat ~/.config/nvim/init.vim 

"set fencs=utf-8,gbk
filetype plugin indent on "especially this line.
syntax on
set laststatus=2
set number
"set anti "macOS anti alias
let g:airline#extensions#tabline#enabled = 1
colorscheme molokai-dark

call plug#begin()
Plug 'scateu/tsv_edl.vim'
Plug 'vim-airline/vim-airline'
call plug#end()

```

```
:PlugInstall
```

```bash
mkdir -p ~/.config/nvim/colors
wget https://github.com/pR0Ps/molokai-dark/raw/master/colors/molokai-dark.vim
```
