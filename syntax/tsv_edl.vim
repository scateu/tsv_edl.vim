" Vim syntax file

if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

if version < 508
  command! -nargs=+ HiLink hi link <args>
else
  command! -nargs=+ HiLink hi def link <args>
endif

syn match tsv_edlEDL	/^\zsEDL\ze\t\d\d:/ conceal cchar=➡
syn match tsv_edlUsed /^---.*$/ conceal cchar=☑
syn match tsv_edlRejected /^xxx.*$/ conceal cchar=X

syn match tsv_edlTimecode	/\t\d\d:\d\d:\d\d[,.:]\d\d\+/ conceal
syn match tsv_edlClipname   /\t|.*|\t/ conceal

syn match tsv_edlHead /^EDL\tRecord In\tRecord Out\tClipname\tSubtitle$/

syn match tsv_edlSpace /\[ SPACE .* secs \]/

syn sync fromstart

HiLink tsv_edlEDL	Comment
HiLink tsv_edlTimecode  Special
HiLink tsv_edlClipname  Identifier
HiLink tsv_edlRejected  NonText
HiLink tsv_edlUsed 	NonText
HiLink tsv_edlHead	Comment
HiLink tsv_edlSpace	Comment

" conceal reference: https://vimjc.com/vim-conceal-text.html
"syn match Concealed '^...\t.*\t|.*|\t' conceal contained
set concealcursor=nvc
hi Conceal ctermfg=109 guifg=#83a598 ctermbg=NONE guibg=NONE

" ['Title', 'Constant', 'Identifier', 'Statement', 'PreProc', 'Type', 'Special']

set cursorline


" =======================
" Org mode style headings
" borrowed from vim-orgmode
" -----------------------
if !exists('g:org_heading_highlight_colors')
	let g:org_heading_highlight_colors = ['Title', 'Constant', 'Identifier', 'Statement', 'PreProc', 'Type', 'Special']
endif

if !exists('g:org_heading_highlight_levels')
	let g:org_heading_highlight_levels = len(g:org_heading_highlight_colors)
endif

let g:org_heading_shade_leading_stars = 0 "Disable g:org_heading_shade_leading_stars, for now
if !exists('g:org_heading_shade_leading_stars')
	let g:org_heading_shade_leading_stars = 1
endif

" Enable Syntax HL:
unlet! s:i s:j s:contains
let s:i = 1
let s:j = len(g:org_heading_highlight_colors)
let s:contains = ' contains=org_timestamp,org_timestamp_inactive,org_subtask_percent,org_subtask_number,org_subtask_percent_100,org_subtask_number_all,org_list_checkbox,org_bold,org_italic,org_underline,org_code,org_verbatim'

if g:org_heading_shade_leading_stars == 1
	let s:contains = s:contains . ',org_shade_stars'
	syntax match org_shade_stars /^\*\{2,\}/me=e-1 contained
	hi def link org_shade_stars Ignore
else
	hi clear org_shade_stars
endif

while s:i <= g:org_heading_highlight_levels
	exec 'syntax match org_heading' . s:i . ' /^\*\{' . s:i . '\}\s.*/' . s:contains
	exec 'hi def link org_heading' . s:i . ' ' . g:org_heading_highlight_colors[(s:i - 1) % s:j]
	let s:i += 1
endwhile
unlet! s:i s:j s:contains

" =======================

let b:current_syntax = "tsv_edl"

delcommand HiLink
" vim: ts=8
