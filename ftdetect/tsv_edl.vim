" Vim filetype detection file
"
augroup tsv_edl
     au! BufRead,BufNewFile *.tsv   call s:test_tsv_edl()
augroup END

fun! s:test_tsv_edl()
  if getline(1) =~ '^EDL.*Record In'
    setfiletype tsv_edl
    return
  endif
  let n = 2
  while n < 20 && n < line("$")
    if getline(n) =~ '^EDL.*\d\d:\d\d:\d\d'
      setfiletype tsv_edl
      return
    endif
    if getline(n) =~ '^---.*\d\d\:\d\d:\d\d'
      setfiletype tsv_edl
      return
    endif
    let n = n + 1
  endwhile
endfun
