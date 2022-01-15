" vi: fdm=marker
if exists("b:did_ftplugin")
    finish
endif
let b:did_ftplugin = 1

let s:save_cpo = &cpo
set cpo&vim

set shell=/bin/bash " macOS. zsh doesn't work
"autoload/tsv_edl.vim  system( socat, jq )

"set shell+=\ -O\ extglob
" see 'man bash'
" > If the extglob shell option is enabled using the shopt builtin
" for the use of ffplay

" MAP KEYBINDINGS
"

"======================
" Toggle Conceal level
"======================
"https://github.com/tpope/vim-unimpaired/issues/105

nmap \c :set <C-R>=&conceallevel ? 'conceallevel=0 wrap' : 'conceallevel=1 nowrap'<CR><CR>

"======================
" Editorial Decision
"======================

"nmap <silent> <cr> yy1gtGpg<tab>0cw---<ESC>0j
"will be mapped after \p is pressed
noremap <silent> \p :call tsv_edl#enter_cherry_pick_mode()<CR>

"horizontally split cherry-pick ~~:sp selection.tsv~~
noremap <silent> \P :call tsv_edl#enter_cherry_pick_mode_horizontally()<CR>

nmap <silent> <backspace> :s/^EDL/xxx/<cr>j
nmap <silent> <delete> :if getline('.') =~# '^EDL' \| s/^EDL/xxx/ \| else \| s/^xxx/EDL/e \| s/^---/EDL/e \| endif<cr>

"======================
" Play and Preview
"======================

" start from cursor, stop at the end


let g:edl_line_pattern = "^EDL\\t\\d\\|^---\\|^xxx"

func! DoTab()
	if (getline(".")  =~# g:edl_line_pattern)
		if g:ipc_media_ready
			call tsv_edl#ipc_play_current_range()
		else
			call tsv_edl#play_current_range()
		endif
	else
		try
			exe "normal! za"
		catch /E490:/
			"no fold, do nothing
		endtry
	endif
endfunc
nnoremap <silent> <tab> :call DoTab()<CR>

func! DoShiftTab()
	if (getline(".")  =~# g:edl_line_pattern)
		if g:ipc_media_ready
			"go to head of subtitle
			execute "normal! 02f|2l"
			call tsv_edl#ipc_play_current_range()
		else
			"go to head of subtitle
			execute "normal! 02f|2l"
			call tsv_edl#play_current_range()
		endif
	else
		if &foldlevel > 1
			set foldlevel=0
		else
			set foldlevel+=1
		endif
	endif
endfunc
" start from head of line, stop at the end
nnoremap <silent> <S-tab> :call DoShiftTab()<CR>

func! DoSlashTab()
	if (getline(".")  =~# g:edl_line_pattern)
		if g:ipc_media_ready
			"do nothing
		else
			call tsv_edl#play_current_range(v:false)
		endif
	else
		"do nothing
	endif
endfunc
" start from cursor, play all along passing the end of this line
nnoremap <silent> \<tab> :call DoSlashTab()<CR>

" Play clips continously from current line if starts with 'EDL'.
" One can press Ctrl-C very hard to stop.
nmap <silent> \<space> 0:call tsv_edl#continous_play()<CR>

"======================
" IPC Seeking & Preview
"======================

" IPC Load media. mpv --no-terminal --input-ipc-server=/tmp/mpvsocket --no-focus-on-open --pause
nmap <silent> \\ 0:call tsv_edl#ipc_init_and_load_media()<CR>

" Play clips continously from current line if starts with 'EDL'.
" One can press Ctrl-C very hard to stop.
"nmap <silent> \<space> 0:call tsv_edl#ipc_continous_play()<CR>

"====================
" Timecode Editing
"====================
" Go to record_in timecode
nnoremap <silent> g9 0f,l

" Go to record_out timecode on the prevous line
nnoremap <silent> g8 0k2f,l

" Go to the start of subtitle
nnoremap <silent> g0 02f\|2l

" append a gap for 5 secs below current line.
nnoremap <silent> gO oEDL	00:00:00,000	00:00:05,000	\| GAP \|	[ SPACE 5.0 secs ]<esc>

nmap <silent> \| :call tsv_edl#break_line()<CR>


func! DoJoin()
	if (getline(".")  =~# g:edl_line_pattern)
		call tsv_edl#join_with_next_line()
	else
		normal! J
	endif
endfunc
nmap <silent> J :call DoJoin()<CR>

" shift the record_in timecode by 1 sec  {{{
nmap <silent> <S-Left> 02f:l<C-X>0?^EDL\\|\\---\\|xxx<CR>02f<Tab>2f:l<C-X>:.,/^EDL\\|---\\|xxx/s/[:\t]\zs\ze\d[,:]/0/ge<CR>/^EDL\\|xxx\\|---/<CR>02f:l
"                                                   ^^ this line and prev EDL line
"                                                  :   s/[:\t]\zs\ze\d[,:]/0/g    do zero padding afterwards
"                      ^^^^^^^^^^ record_in
"                                ^^^^^^^^^^^^^^^^^^ previous line, record_out
"
"nmap <silent> <S-Right> 02f:l<C-A>k02f<Tab>2f:l<C-A>j:?^EDL\|---\|xxx?.-1,.s/[:\t]\zs\ze\d[,:]/0/ge<CR>02f:l
nmap <silent> <S-Right> 02f:l<C-A>0?^EDL\\|\\---\\|xxx<CR>02f<Tab>2f:l<C-A>:.,/^EDL\\|---\\|xxx/s/[:\t]\zs\ze\d[,:]/0/ge<CR>/^EDL\\|xxx\\|---/<CR>02f:l

" {{{2
" shift the record_out timecode by 1 sec FIXME map doen't work
"nmap <silent> <S-Up> 02f<Tab>2f:ll<C-X>
"nmap <silent> <S-Down> 02f<Tab>2f:ll<C-A>
" }}}2

" }}}

"====================
" Export & Render
"====================
"vnoremap <space> :'<,'>w !tsv2roughcut<CR>
vnoremap <space> :w !tsv2roughcut --user-input-newname<CR>


set nrformats=
" only decimal

set guioptions=aiAe "for macVim
" https://stackoverflow.com/questions/12177686/how-do-i-get-macvim-tabs-to-display-graphically/30108155

set wrap linebreak "to avoid words broken into characters
if &conceallevel == 0 | set wrap | else | set nowrap | endif

"set so=10 "scrolloff , center
set noexpandtab

" Indent
" borrowed from https://stackoverflow.com/questions/3828606/vim-markdown-folding
" and vim-orgmode/indent/
function Markdown_and_Org_Level()
	let h = matchstr(getline(v:lnum), '^[\*|#]\+')
	if empty(h)
		return "="
	else
		return ">" . len(h)
	endif
endfunction

"Folding Behavior {{{
"set fdm=marker
"set foldopen=all
"set foldclose=all
" }}}

"setlocal foldtext=GetOrgFoldtext()
setlocal fillchars-=fold:-
setlocal fillchars+=fold:.

" https://github.com/chrisbra/vim_dotfiles/blob/master/plugin/CustomFoldText.vim
" Customized version of folded text, idea by
" http://www.gregsexton.org/2011/03/improving-the-text-displayed-in-a-fold/
fu! CustomFoldText(string) "{{{1
    "get first non-blank line
    let fs = v:foldstart
    if getline(fs) =~ '^\s*$'
      let fs = nextnonblank(fs + 1)
    endif
    if fs > v:foldend
        let line = getline(v:foldstart)
    else
        let line = substitute(getline(fs), '\t', repeat(' ', &tabstop), 'g')
    endif
    let pat  = matchstr(&l:cms, '^\V\.\{-}\ze%s\m')
    " remove leading comments from line
    let line = substitute(line, '^\s*'.pat.'\s*', '', '')
    " remove foldmarker from line
    let pat  = '\%('. pat. '\)\?\s*'. split(&l:fmr, ',')[0]. '\s*\d\+'
    let line = substitute(line, pat, '', '')

"   let line = substitute(line, matchstr(&l:cms,
"	    \ '^.\{-}\ze%s').'\?\s*'. split(&l:fmr,',')[0].'\s*\d\+', '', '')

    let w = get(g:, 'custom_foldtext_max_width', winwidth(0)) - &foldcolumn - (&number ? 8 : 0)
    let foldSize = 1 + v:foldend - v:foldstart
    let foldSizeStr = " " . foldSize . " lines "
    let foldLevelStr = '+'. v:folddashes
    let lineCount = line("$")
    if has("float")
	try
	    let foldPercentage = printf("[%.1f", (foldSize*1.0)/lineCount*100) . "%] "
	catch /^Vim\%((\a\+)\)\=:E806/	" E806: Using Float as String
	    let foldPercentage = printf("[of %d lines] ", lineCount)
	endtry
    endif
    if exists("*strwdith")
	let expansionString = repeat(a:string, w - strwidth(foldSizeStr.line.foldLevelStr.foldPercentage))
    else
	let expansionString = repeat(a:string, w - strlen(substitute(foldSizeStr.line.foldLevelStr.foldPercentage, '.', 'x', 'g')))
    endif
    return line . expansionString . foldSizeStr . foldPercentage . foldLevelStr
endf

set foldtext=CustomFoldText('.')


setlocal foldexpr=Markdown_and_Org_Level()
setlocal foldmethod=expr

"setlocal indentexpr=GetOrgIndent()
setlocal nolisp
setlocal nosmartindent
setlocal autoindent

"-----------------------------
"following code are borrowed from
"https://github.com/arp242/jumpy.vim/
"-----------------------------

let g:jumpy_map = [']]', '[[', 'g]', 'g[']
let g:jumpy_after = ''
"https://github.com/arp242/jumpy.vim/blob/master/autoload/jumpy.vim
fun! tsv_edl#jumpy_map(decl, stmt) abort
	let l:map = get(g:, 'jumpy_map', [']]', '[[', 'g]', 'g['])
	if l:map is 0
		return
	endif

	let l:after = get(g:, 'jumpy_after', '')

	if l:map[0] isnot# '' && l:map[1] isnot# '' && a:decl isnot# ''
		for l:mode in ['n', 'o', 'x']
			exe printf('%snoremap <buffer> <silent> %s :<C-u>call tsv_edl#jumpy_jump("%s", "%s", "next")<CR>%s',
						\ l:mode, l:map[0], fnameescape(a:decl), l:mode, l:after)
			exe printf('%snoremap <buffer> <silent> %s :<C-u>call tsv_edl#jumpy_jump("%s", "%s", "prev")<CR>%s',
						\ l:mode, l:map[1], fnameescape(a:decl), l:mode, l:after)
		endfor
	endif

	if l:map[2] isnot# '' && l:map[3] isnot# '' && a:stmt isnot# ''
		for l:mode in ['n', 'o', 'x']
			exe printf('%snoremap <buffer> <silent> %s :<C-u>call tsv_edl#jumpy_jump("%s", "%s", "next")<CR>%s',
						\ l:mode, l:map[2], fnameescape(a:stmt), l:mode, l:after)
			exe printf('%snoremap <buffer> <silent> %s :<C-u>call tsv_edl#jumpy_jump("%s", "%s", "prev")<CR>%s',
						\ l:mode, l:map[3], fnameescape(a:stmt), l:mode, l:after)
		endfor
	endif
endfun

fun! tsv_edl#jumpy_jump(pattern, mode, dir) abort
	" Get motion count; done here as some commands later on will reset it.
	let l:count = v:count1

	" Set context mark so user can jump back with '' or ``.
	normal! m'

	" Start visual selection or re-select previously selected.
	if a:mode is# 'x'
		normal! gv
	endif

	let l:save = winsaveview()
	for l:i in range(l:count)
		let l:loc = search(a:pattern, 'Wz' . (a:dir is# 'prev' ? 'b' : ''))
		if l:loc > 0
			" Jump to first non-whitespace if cursor is on leading whitespace.
			if getline('.')[:col('.') - 1] =~# '^\s*$'
				normal! ^
			endif
			continue
		endif

		" Jump to top or bottom of file if we're at the first or last match.
		if l:i is l:count - 1
			exe 'keepjumps normal! ' . (a:dir is# 'next' ? 'G' : 'gg')
		else
			call winrestview(l:save)
		endif

		break
	endfor
endfun

"https://github.com/arp242/jumpy.vim/blob/master/after/ftplugin/markdown.vim
call tsv_edl#jumpy_map('\v%(^*{1,7}|^\=\=\=|^---|^#{1,7})', '')

