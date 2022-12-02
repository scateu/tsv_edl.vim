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

syn match tsv_edlEDL	/^\zsEDL\ze\t\d\d:/ conceal cchar=>
syn match tsv_edlUsed /^---.*$/ conceal cchar=-
syn match tsv_edlRejected /^xxx.*$/ conceal cchar=x

syn match tsv_edlTimecode	/\t\d\d:\d\d:\d\d[,.:]\d\d\+/ conceal
syn match tsv_edlClipname   /\t|.*|\t/ conceal

syn match tsv_edlHead /^EDL\tRecord In\tRecord Out\tClipname\tSubtitle$/

syn match tsv_edlSpace /\[ SPACE .* secs \]/
syn match tsv_edlNewline /\\N/ conceal cchar=_

syn match    markdownHeader1     "^# .*$"
syn match    markdownHeader2     "^## .*$"
syn match    markdownHeader3     "^### .*$"
syn match    markdownHeader4     "^#### .*$"
syn match    markdownHeader5     "^##### .*$"
syn match    markdownHeader6     "^###### .*$"
syn match    markdownHeader7     "^####### .*$"


syn match    orgHeader1     "^\* .*$"
syn match    orgHeader2     "^\*\* .*$"
syn match    orgHeader3     "^\*\*\* .*$"
syn match    orgHeader4     "^\*\*\*\* .*$"
syn match    orgHeader5     "^\*\*\*\*\* .*$"
syn match    orgHeader6     "^\*\*\*\*\*\* .*$"
syn match    orgHeader7     "^\*\*\*\*\*\*\* .*$"


if 0
	highlight markdownHeader1 ctermfg=34
	highlight markdownHeader2 ctermfg=32
	highlight markdownHeader3 ctermfg=127
	highlight markdownHeader4 ctermfg=45
	highlight markdownHeader5 ctermfg=220

	highlight orgHeader1 ctermfg=34
	highlight orgHeader2 ctermfg=32
	highlight orgHeader3 ctermfg=127
	highlight orgHeader4 ctermfg=45
	highlight orgHeader5 ctermfg=220
else
	HiLink markdownHeader1 Title
	HiLink markdownHeader2 Constant
	HiLink markdownHeader3 Identifier
	HiLink markdownHeader4 Statement
	HiLink markdownHeader5 PreProc
	HiLink markdownHeader6 Type
	HiLink markdownHeader7 Special

	HiLink orgHeader1 Title
	HiLink orgHeader2 Constant
	HiLink orgHeader3 Identifier
	HiLink orgHeader4 Statement
	HiLink orgHeader5 PreProc
	HiLink orgHeader6 Type
	HiLink orgHeader7 Special
endif

HiLink tsv_edlEDL	Comment
HiLink tsv_edlTimecode  Special
HiLink tsv_edlClipname  Identifier
HiLink tsv_edlRejected  NonText
HiLink tsv_edlUsed 	NonText
HiLink tsv_edlHead	Comment
HiLink tsv_edlSpace	Comment
HiLink tsv_edlNewline	Comment


" conceal reference: https://vimjc.com/vim-conceal-text.html
"syn match Concealed '^...\t.*\t|.*|\t' conceal contained
set concealcursor=nvc
hi Conceal ctermfg=LightBlue guifg=#83a598 ctermbg=NONE guibg=NONE

" ['Title', 'Constant', 'Identifier', 'Statement', 'PreProc', 'Type', 'Special']

set cursorline
"hi CursorLine guibg=#1C1C1C gui=NONE ctermbg=234 cterm=NONE
hi CursorLine guibg=Grey40 gui=NONE ctermbg=237 cterm=NONE
"https://vi.stackexchange.com/questions/23066/change-cursorline-style

syn sync fromstart


" =======================
" Org mode style headings
" borrowed from vim-orgmode
" -----------------------
"if !exists('g:org_heading_highlight_colors')
"	let g:org_heading_highlight_colors = ['Title', 'Constant', 'Identifier', 'Statement', 'PreProc', 'Type', 'Special']
"endif
"
"if !exists('g:org_heading_highlight_levels')
"	let g:org_heading_highlight_levels = len(g:org_heading_highlight_colors)
"endif
"
"
"let g:org_heading_shade_leading_stars = 0 
"Disable g:org_heading_shade_leading_stars, for now
"
"if !exists('g:org_heading_shade_leading_stars')
"	let g:org_heading_shade_leading_stars = 1
"endif
"
" Enable Syntax HL
"
"unlet! s:i s:j s:contains
"let s:i = 1
"let s:j = len(g:org_heading_highlight_colors)
"let s:contains = ' contains=org_timestamp,org_timestamp_inactive,org_subtask_percent,org_subtask_number,org_subtask_percent_100,org_subtask_number_all,org_list_checkbox,org_bold,org_italic,org_underline,org_code,org_verbatim'
"
"if g:org_heading_shade_leading_stars == 1
"	let s:contains = s:contains . ',org_shade_stars'
"	syntax match org_shade_stars /^\*\{2,\}/me=e-1 contained
"	hi def link org_shade_stars Ignore
"else
"	hi clear org_shade_stars
"endif
"
"while s:i <= g:org_heading_highlight_levels
"	exec 'syntax match org_heading' . s:i . ' /^\*\{' . s:i . '\}\s.*/' . s:contains
"	exec 'hi def link org_heading' . s:i . ' ' . g:org_heading_highlight_colors[(s:i - 1) % s:j]
"	let s:i += 1
"endwhile
"unlet! s:i s:j s:contains

" =======================

let b:current_syntax = "tsv_edl"

delcommand HiLink
" vim: ts=8
