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
call plug#begin()
Plug 'scateu/tsv_edl.vim'
call plug#end()

```

```
:PlugInstall
```
