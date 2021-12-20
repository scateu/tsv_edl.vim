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

syn match tsv_edlEDL	/^EDL/ conceal 
syn match tsv_edlTimecode	/\d\d:\d\d:\d\d[,.:]\d\d\+/ conceal
syn match tsv_edlUsed /^---.*$/ conceal cchar=-
syn match tsv_edlRejected /^xxx.*$/ conceal cchar=x
syn match tsv_edlClipname   /\t|.*|\t/ conceal

set concealcursor=nvic
set cursorline

syn sync fromstart

HiLink tsv_edlEDL	Comment
HiLink tsv_edlTimecode  Special
HiLink tsv_edlClipname  Identifier
"HiLink tsv_edlUsed 	Comment
HiLink tsv_edlRejected  NonText
HiLink tsv_edlUsed 	NonText

" ['Title', 'Constant', 'Identifier', 'Statement', 'PreProc', 'Type', 'Special']


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
