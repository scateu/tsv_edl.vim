# Search for notes in a long tsv\_edl file, between 'EDL's

```
/^[^E][^D][^L]
```
means match every line not starts with `EDL`

or

```
:nmap <silent> g] /^[^E*#][^D][^L]<cr>
:nmap <silent> g[ /^[^E*#][^D][^L]<cr>
```

# TIPS: make cursor line more distinguishable

```
:hi CursorLine   cterm=NONE ctermbg=darkred ctermfg=white guibg=darkred guifg=white
```
