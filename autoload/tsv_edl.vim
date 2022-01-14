function! tsv_edl#timecode_to_secs(timecode)
	let _tc = split(substitute(a:timecode, ',' , '.', 'g'), ":")
	let HH = str2nr(_tc[0])
	let MM = str2nr(_tc[1])
	let SS = str2float(_tc[2])
	return HH*3600.0+MM*60.0+SS
endfunction

function! tsv_edl#sec_to_timecode(sec)
	if a:sec < 0
		return ("00:00:00.000")
	endif
	let HH = float2nr(a:sec/3600.0)
	let MM = float2nr((a:sec - HH*3600.0)/60.0)
	let SS = float2nr((a:sec - HH*3600.0 - MM*60.0))
	let MS = float2nr((a:sec - HH*3600.0 - MM*60.0 - SS)*1000.0)
	return printf("%02d:%02d:%02d.%03d", HH, MM, SS, MS)
endfunction


function! tsv_edl#infer_time_pos(line)
	"""""" infer current timecode
	let cursor_pos = getpos(".")[2]  "41
	let words_start_pos = matchstrpos(a:line, '|\t', 32, 1)[-1]  + 1.0
	let b = len(a:line) - words_start_pos
	if b <= 0 
		return 0
	endif
	let a = cursor_pos - words_start_pos  "41 - 43
	let _p = a / b
	" FIXME wide chars
	let _p = _p > 0 ? _p : 0
	return _p
endfunction

function! tsv_edl#play_current_range(stop_at_end = v:true)
	let line=getline('.')
	if len(line) > 0
		let line_list = split(line, '\t')
		if line_list[0] == 'EDL' || line_list[0] == '---' || line_list[0] == 'xxx'
			let filename = trim(line_list[3],'|')
			let filename = trim(filename)
			let record_in = substitute(line_list[1], ',' , '.', 'g') 
			let record_out = substitute(line_list[2], ',' , '.', 'g') 
			"let command = 'ffplay -hide_banner -ss ' . record_in . ' ./*"' . filename . '"' . '*.!(tsv|srt|txt)'

			let cursor_pos_percentage = tsv_edl#infer_time_pos(line)

			"echo "[cursor_pos_percentage]: ".float2nr(cursor_pos_percentage*100)."%"
			let _rec_in_secs = tsv_edl#timecode_to_secs(record_in)
			let _rec_out_secs = tsv_edl#timecode_to_secs(record_out)
			let line_duration =  _rec_out_secs - _rec_in_secs
			let deduced_line_duration = line_duration * ( 1 - cursor_pos_percentage)
			"echo printf("[_rec_in_secs, _rec_out_secs, line_duration, deduced_line_duration]: %.3f, %.3f, %.3f, %.3f", _rec_in_secs, _rec_out_secs, line_duration, deduced_line_duration)
			let deduced_start_pos_secs = line_duration * cursor_pos_percentage + _rec_in_secs
			"echo "[deduced_start_pos_secs]: ". printf("%.3f", deduced_start_pos_secs)
			"
			let deduced_timecode = tsv_edl#sec_to_timecode(deduced_start_pos_secs)
			"echo "[deduced_timecode]: ". deduced_timecode

			"""""" command, go!
			"let command_play_from_start = 'ffplay -hide_banner -noborder -seek_interval 1 -ss ' . record_in . ' ./*"' . filename . '"' . '*.!(tsv|srt|txt)&'
			"let command_play_from_cursor = printf('ffplay -autoexit -hide_banner -noborder -seek_interval 1 -ss %s -t %.3f ./*"%s"*.!(tsv|srt|txt)', deduced_start_pos_secs, deduced_line_duration, filename)
			"let command_mpv_from_cursor = 'mpv --profile=low-latency --no-terminal --start='. deduced_timecode . ' --end='. record_out . ' ./*"' . filename . '"' . '*.!(tsv|srt|txt)'

			if a:stop_at_end == v:true
				let command_mpv_from_cursor = 'mpv --no-terminal --start='. deduced_timecode . ' --end='. record_out . ' "$(ls *"' . filename . '"* | ' . " sed '/srt$/d; /tsv$/d; /txt$/d;' | head -n1)\""
				" on the nested quote inside brackets
				" > Once one is inside $(...), quoting starts all over from scratch.
				" -- https://unix.stackexchange.com/questions/289574/nested-double-quotes-in-assignment-with-command-substitution
				"
				" --profile=low-latency 
				"echo '[Ctrl-C to stop.] '
				let prompt = "[mpv] " . filename . " " . deduced_timecode . " --> " . record_out
			else
				let command_mpv_from_cursor = 'mpv --no-terminal --start='. deduced_timecode . ' "$(ls *"' . filename . '"* | ' . " sed '/srt$/d; /tsv$/d; /txt$/d;' | head -n1)\""
				let prompt = "[mpv] " . filename . " " . deduced_timecode . " --> EOF"
			endif

			let command = command_mpv_from_cursor
			echo prompt
			call system(command)

			"silent execute "!".command
			redraw!
		endif
	endif
endfunction

function! tsv_edl#continous_play()
	call cursor(0,1) " current line, first column
	let next_line_number = search('^EDL', 'ncW')
	while next_line_number > 0
		call cursor(next_line_number, 1) " next line, first column
		redraw!
		call tsv_edl#play_current_range() 
		let next_line_number = search('^EDL', 'nW')
	endwhile
	" Reference {{{
	" https://stackoverflow.com/questions/22868834/how-can-i-execute-a-command-until-the-end-of-the-file-in-vim/22869952
	" You can write an explicit loop that stops when it reaches the last line:
	"     :while line('.') < line('$') | exe 'normal! 3Jj' | endwhile
	" Or you could just rely on the command sequence aborting when there are no more lines, and create a sufficiently long sequence:
	":    exe 'normal!' repeat('3Jj', 100)
	" }}}
endfunction

function! tsv_edl#break_line()
	let line=getline('.')
	if len(line) > 0
		let line_list = split(line, '\t')
		if line_list[0] == 'EDL' || line_list[0] == '---' || line_list[0] == 'xxx'
			let cursor_pos_percentage = tsv_edl#infer_time_pos(line)

			let _rec_in_secs = tsv_edl#timecode_to_secs(line_list[1])
			let _rec_out_secs = tsv_edl#timecode_to_secs(line_list[2])
			let line_duration =  _rec_out_secs - _rec_in_secs
			let deduced_start_pos_secs = line_duration * cursor_pos_percentage + _rec_in_secs
			"echo "[deduced_start_pos_secs]: ". printf("%.3f", deduced_start_pos_secs)
			let deduced_timecode = substitute(tsv_edl#sec_to_timecode(deduced_start_pos_secs), '\.', ',', 'g')
			"echo "[deduced_timecode]: ". deduced_timecode

			let words_start_pos = matchstrpos(line, '|\t', 32, 1)[-1] + 1
			"echo words_start_pos
			let break_pos = getpos(".")[2]

			let break_pos_relative  = break_pos - words_start_pos
			if break_pos_relative < 0
				echo "not a good break choice"
				return
			endif

			let _cur_words = line_list[4][:break_pos_relative-1]
			let _next_words = line_list[4][break_pos_relative:]

			let _cur_in = line_list[1]
			let _cur_out = line_list[2]

			let _cur_line = printf("%s\t%s\t%s\t%s\t%s",line_list[0], line_list[1], deduced_timecode, line_list[3], _cur_words)
			let _next_line = printf("%s\t%s\t%s\t%s\t%s",line_list[0], deduced_timecode, line_list[2], line_list[3], _next_words)

			call setline(".",_cur_line )
			call append(".", _next_line)
		endif
	endif
endfunction

function!  tsv_edl#join_with_next_line()
	let cur_line=getline('.')
	let next_line=getline(line('.')+1)
	let cur_line_end_col = col('$') "record the pos of EOL

	if len(cur_line) > 0 && len(next_line) > 0
		let cur_line_list = split(cur_line, '\t')
		let next_line_list = split(next_line, '\t')

		if (cur_line_list[0] == 'EDL' || cur_line_list[0] == '---' || cur_line_list[0] == 'xxx') 
					\ && (next_line_list[0] == 'EDL' || next_line_list[0] == '---' || next_line_list[0] == 'xxx')
			let tc1 = tsv_edl#timecode_to_secs(cur_line_list[2])
			let tc2 = tsv_edl#timecode_to_secs(next_line_list[1])

			if (tc2 < tc1)
				echohl WarningMsg
				echo "Refuse to join a gap with reversed time-space"
				echohl None
				return
			endif
			if (tc2 - tc1 > 10)
				echohl WarningMsg
				echo "Refuse to join a gap longer than 10 sec"
				echohl None
				return
			endif

			let a = cur_line_list[0]
			let b = cur_line_list[1]
			let c = next_line_list[2]
			if cur_line_list[3] !=# next_line_list[3]
				echohl WarningMsg
				echo "Cannot join clips from different media"
				echohl None
				return
			endif

			let d = cur_line_list[3]
			if (next_line_list[4] =~# "^[ SPACE ")
				let e = cur_line_list[4]
			else
				let e = cur_line_list[4] .' '. next_line_list[4]
			endif

			let new_line = printf("%s\t%s\t%s\t%s\t%s",a,b,c,d,e)
			call setline(".", new_line )
			call setline(line(".")+1, "")
			execute "normal! jddk"
			call cursor(0, cur_line_end_col) "place cursor right between the joined lines
			echo "Clips joined."
		endif
	endif
endfunction

"" see !shopt
""     extglob off

"======================
" IPC
"======================

let g:ipc_media_ready = v:false
let g:ipc_loaded_media_name = ""
let g:ipc_timecode = ""

function! tsv_edl#ipc_load_media(filename)

	"calculate deduced timecode
	let line=getline('.')
	if len(line) == 0 | return | endif
	let line_list = split(line, '\t')
	if len(line_list) == 0 | return | endif
	if ! (line_list[0] == 'EDL' || line_list[0] == '---' || line_list[0] == 'xxx') | return | endif
	if line_list[1] !~# '\d\d:\d\d:\d\d,\d\d\d' | return | endif
	let record_in = substitute(line_list[1], ',' , '.', 'g') 
	let record_out = substitute(line_list[2], ',' , '.', 'g') 
	let cursor_pos_percentage = tsv_edl#infer_time_pos(line)
	let _rec_in_secs = tsv_edl#timecode_to_secs(record_in)
	let _rec_out_secs = tsv_edl#timecode_to_secs(record_out)
	let line_duration =  _rec_out_secs - _rec_in_secs
	let deduced_line_duration = line_duration * ( 1 - cursor_pos_percentage)
	let deduced_start_pos_secs = line_duration * cursor_pos_percentage + _rec_in_secs
	let deduced_timecode = tsv_edl#sec_to_timecode(deduced_start_pos_secs)
	let g:ipc_timecode = tsv_edl#sec_to_timecode(deduced_start_pos_secs)

	let filename_with_ext = trim(system('ls *"' . a:filename . '"* | ' . " sed '/srt$/d; /tsv$/d; /txt$/d;' | head -n1"))
	echon "[ipc_load_media] loading " . filename_with_ext

	call system('echo "{ \"command\": [\"loadfile\", \"' . filename_with_ext . '\", \"replace\", \"start=' . string(deduced_start_pos_secs) . '\" ] }" | socat - /tmp/mpvsocket 2>/dev/null')
	let g:ipc_loaded_media_name = a:filename
	" seek again
	"let command = 'echo "{ \"command\": [\"set_property\", \"playback-time\", ' . string(deduced_start_pos_secs) . ' ] }" | socat - /tmp/mpvsocket > /dev/null'
	"let prompt = "[mpv ipc] load new clip, then seek to " . string(deduced_start_pos_secs) . "  "
	"sleep 400m
	"echon prompt
	"call system(command)
endfunction

function! tsv_edl#ipc_init_and_load_media(pause = v:true)
	if g:ipc_media_ready
		call tsv_edl#ipc_quit()
		return
	endif

	" go to a valid line
	if (getline(".")  !~# g:edl_line_pattern)
		call cursor(0,1) " current line, first column
		call search(g:edl_line_pattern, 'cW')
		call tsv_edl#try_open_fold()
	endif
 
	nmap <silent> <space> :call tsv_edl#ipc_toggle_play()<CR>
	nmap <silent> \<space> 0:call tsv_edl#ipc_continous_play()<CR>

	" control mpv with mpvc, seek with mpvc
	" mpv --input-ipc-server=/tmp/mpvsocket
	" wget https://raw.githubusercontent.com/lwilletts/mpvc/master/mpvc
	nmap <silent> <Up> k:call tsv_edl#ipc_seek()<CR>
	nmap <silent> <Down> j:call tsv_edl#ipc_seek()<CR>
	nmap <silent> <Left> h:call tsv_edl#ipc_seek()<CR>
	nmap <silent> <Right> l:call tsv_edl#ipc_seek()<CR>
	nmap <silent> s :call tsv_edl#ipc_seek()<CR>
	"nmap <silent> S n:call tsv_edl#ipc_seek()<CR>
	"nmap <silent> <tab> :call tsv_edl#ipc_play_current_range()<CR>
	"nmap <silent> <S-tab> g0:call tsv_edl#ipc_play_current_range()<CR>
	nmap <silent> S :call tsv_edl#ipc_sync_playhead()<CR>
	nmap <silent> \S :call tsv_edl#ipc_sync_playhead(v:true)<CR>
	nmap <silent> gi :call tsv_edl#write_record_in()<CR>
	nmap <silent> go :call tsv_edl#write_record_out()<CR>

	if g:cherry_pick_mode_entered
		echon "already in cherry_pick_mode, do not map Enter to seek"
	else
		noremap <silent> <cr> :call tsv_edl#ipc_seek()<CR>
		let g:cr_map_status = "[⏎ = seek] "
	endif


	if system("pgrep -f input-ipc-server=/tmp/mpvsocket")
		echon '[pgrep] existing mpvsocket found, reuse. '
		let result=trim(system('echo "{ \"command\": [\"get_property\", \"filename\" ] }" | socat - /tmp/mpvsocket 2>/dev/null | jq -r .data'))
		"echo result
		let clipname = fnamemodify(result, ":r")
		"echo clipname
		let g:ipc_media_ready = v:true
		let g:ipc_loaded_media_name = clipname
		"call tsv_edl#ipc_seek()
		call tsv_edl#ipc_sync_playhead()
		call tsv_edl#try_open_fold()
		return
	endif

	let line=getline('.')
	if len(line) == 0 | return | endif

	let line_list = split(line, '\t')
	if len(line_list) == 0 | return | endif
	if ! (line_list[0] == 'EDL' || line_list[0] == '---' || line_list[0] == 'xxx') | return | endif
	if line_list[1] !~# '\d\d:\d\d:\d\d,\d\d\d' | return | endif

	let filename = trim(trim(line_list[3],'|'))

	let start_tc_in_HHMMSSMS = substitute(line_list[1], ',' , '.', 'g')
	let start_tc = string(tsv_edl#timecode_to_secs(start_tc_in_HHMMSSMS))

	let g:ipc_timecode = start_tc_in_HHMMSSMS 
	
	let command = 'mpv --autofit-larger=90%x80% --ontop --no-terminal --keep-open=always --input-ipc-server=/tmp/mpvsocket --no-focus-on-open --start=' . start_tc 
	if a:pause
		let command = command . ' --pause' 
		let g:ipc_pause = v:true
	else
		let g:ipc_pause = v:false
	endif
	let command = command . ' "$(ls *"' . filename . '"* | ' . " sed '/srt$/d; /tsv$/d; /txt$/d;' | head -n1)\"" . " &"
	"echo command
	echon "[mpv] load media: " . filename
	call system(command)
	if v:shell_error
		" FIXME doen't work for now
		echon '[mpv] could not load media. '
		let g:ipc_media_ready = v:false
		let g:ipc_loaded_media_name = ""
	else
		let g:ipc_media_ready = v:true
		let g:ipc_loaded_media_name = filename
		"sleep 500m
		"call tsv_edl#ipc_seek()
	endif
endfunction

function! tsv_edl#ipc_quit()
	let command_ipc_quit = 'echo "{ \"command\": [\"quit\"] }" | socat - /tmp/mpvsocket > /dev/null &'
	let command_pkill = "pkill -f input-ipc-server=/tmp/mpvsocket"
	call system(command_ipc_quit)
	let g:ipc_media_ready = v:false
	let g:ipc_loaded_media_name = ""
	echon "[mpv ipc] quit. "

	"restore key mappings
	nmap <silent> \<space> 0:call tsv_edl#continous_play()<CR>
	unmap <Up>
	unmap <Down>
	unmap <Left>
	unmap <Right>
	unmap s
	unmap S
	unmap \S
	unmap gi
	unmap go
	"nnoremap <silent> <tab> :call tsv_edl#play_current_range()<CR>
	"nnoremap <silent> <S-tab> 02f\|2l:call tsv_edl#play_current_range()<CR>

	unmap <cr>
	let g:cr_map_status = "[⏎ = ⏎]"
	let g:cherry_pick_mode_entered = v:false "for now, it stands for enter key remapped to 'pick'
endfunction

function! tsv_edl#ipc_toggle_play()
	let result=trim(system('echo "{ \"command\": [\"get_property\", \"pause\" ] }" | socat - /tmp/mpvsocket 2>/dev/null | jq -r .data'))

	if result ==? "true"
		call tsv_edl#ipc_always_play()
	elseif result ==? "false"
		call tsv_edl#ipc_always_pause()
	endif
endfunction

function! tsv_edl#ipc_always_pause()
	call system('echo "{ \"command\": [\"set_property\", \"pause\", true ] }" | socat - /tmp/mpvsocket > /dev/null &')
	let playback_time=tsv_edl#ipc_get_playback_time()
	let playback_time_in_timecode = tsv_edl#sec_to_timecode(str2float(playback_time))
	let g:ipc_timecode = "[" . playback_time_in_timecode . "]"
	echo "[mpv ipc] paused at: " .. playback_time_in_timecode
	let g:ipc_pause = v:true
endfunction
function! tsv_edl#ipc_always_play()
	call system('echo "{ \"command\": [\"set_property\", \"pause\", false ] }" | socat - /tmp/mpvsocket > /dev/null &')
	echo "[mpv ipc] PLAY"
	let g:ipc_pause = v:false
endfunction

function! tsv_edl#ipc_play_current_range()
	"mapped to tab key
	"for now: simply seek() and play()
	
	if ! (getline(".")  =~# "^EDL\\|^---\\|^xxx")
		call search("^EDL\\|^---\\|^xxx")
	endif

	call tsv_edl#ipc_seek()
	call tsv_edl#ipc_always_play()
endfunction

function! tsv_edl#ipc_seek()
	if ! g:ipc_media_ready  " since arrow keys will be unbound. This condition will never be met
		echon "[mpv ipc] not loaded. press \\\\ to init or connect."
		return
	endif

	let _go_back_line_number = 0
	if (getline(".")  !~# g:edl_line_pattern)
		let _go_back_line_number = line('.')
		call cursor(0,1) " current line, first column
		call search(g:edl_line_pattern, 'cW')
		" imagine, on folded 'Chapter' tree
		" press [Enter]
		" cursor is moved to the first EDL line without being noticed.
	endif

	let line=getline('.')
	if len(line) == 0 | return | endif

	let line_list = split(line, '\t')
	if len(line_list) == 0 | return | endif
	if ! (line_list[0] == 'EDL' || line_list[0] == '---' || line_list[0] == 'xxx') | return | endif
	if line_list[1] !~# '\d\d:\d\d:\d\d,\d\d\d' | return | endif

	let filename = trim(trim(line_list[3],'|'))

	if filename !=# g:ipc_loaded_media_name
		echon "[mpv ipc] different media, load new. "
		call tsv_edl#ipc_load_media(filename)
	endif

	let record_in = substitute(line_list[1], ',' , '.', 'g') 
	let record_out = substitute(line_list[2], ',' , '.', 'g') 

	let cursor_pos_percentage = tsv_edl#infer_time_pos(line)

	"echo "[cursor_pos_percentage]: ".float2nr(cursor_pos_percentage*100)."%"
	let _rec_in_secs = tsv_edl#timecode_to_secs(record_in)
	let _rec_out_secs = tsv_edl#timecode_to_secs(record_out)
	let line_duration =  _rec_out_secs - _rec_in_secs
	let deduced_line_duration = line_duration * ( 1 - cursor_pos_percentage)
	"echo printf("[_rec_in_secs, _rec_out_secs, line_duration, deduced_line_duration]: %.3f, %.3f, %.3f, %.3f", _rec_in_secs, _rec_out_secs, line_duration, deduced_line_duration)
	let deduced_start_pos_secs = line_duration * cursor_pos_percentage + _rec_in_secs
	"echo "[deduced_start_pos_secs]: ". printf("%.3f", deduced_start_pos_secs)
	"
	let deduced_timecode = tsv_edl#sec_to_timecode(deduced_start_pos_secs)
	let g:ipc_timecode = deduced_timecode
	"echo "[deduced_timecode]: ". deduced_timecode

	"let command = 'mpvc -T '. string(deduced_start_pos_secs)  . ' &'
	let command = 'echo "{ \"command\": [\"set_property\", \"playback-time\", ' . string(deduced_start_pos_secs) . ' ] }" | socat - /tmp/mpvsocket > /dev/null &'
	" socat can be replaced by: nc -U -N $SOCKET
	let prompt = "[mpv ipc] seek to " . string(deduced_timecode) . "  "

	echon prompt
	call system(command)

	"silent execute "!".command
	redraw!
	if _go_back_line_number != 0
		"cursor being move to next valid line without being noticed. 
		"go back now.
		call cursor(_go_back_line_number,1)
	endif
endfunction

function! tsv_edl#ipc_continous_play()
	call cursor(0,1) " current line, first column
	let next_line_number = search('^EDL', 'ncW')

	call tsv_edl#ipc_always_play()

	while next_line_number > 0
		call cursor(next_line_number, 1) " next line, first column
		redraw!
		let line=getline('.')
		if len(line) > 0
			let line_list = split(line, '\t')
			if line_list[0] == 'EDL' || line_list[0] == '---' "|| line_list[0] == 'xxx'
				let filename = trim(trim(line_list[3],'|'))

				if filename !=# g:ipc_loaded_media_name
					echon "[mpv ipc] different media, load new. "
					call tsv_edl#ipc_load_media(filename)
					call tsv_edl#ipc_always_play()
				endif

				let record_in = substitute(line_list[1], ',' , '.', 'g') 
				let record_out = substitute(line_list[2], ',' , '.', 'g') 

				let cursor_pos_percentage = tsv_edl#infer_time_pos(line)

				"echo "[cursor_pos_percentage]: ".float2nr(cursor_pos_percentage*100)."%"
				let _rec_in_secs = tsv_edl#timecode_to_secs(record_in)
				let _rec_out_secs = tsv_edl#timecode_to_secs(record_out)
				let line_duration =  _rec_out_secs - _rec_in_secs
				let deduced_line_duration = line_duration * ( 1 - cursor_pos_percentage)
				"echo printf("[_rec_in_secs, _rec_out_secs, line_duration, deduced_line_duration]: %.3f, %.3f, %.3f, %.3f", _rec_in_secs, _rec_out_secs, line_duration, deduced_line_duration)
				let deduced_start_pos_secs = line_duration * cursor_pos_percentage + _rec_in_secs
				"echo "[deduced_start_pos_secs]: ". printf("%.3f", deduced_start_pos_secs)
				"
				let deduced_timecode = tsv_edl#sec_to_timecode(deduced_start_pos_secs)
				"echo "[deduced_timecode]: ". deduced_timecode
				let g:ipc_timecode = deduced_timecode

				let command = 'echo "{ \"command\": [\"set_property\", \"playback-time\", ' . string(deduced_start_pos_secs) . ' ] }" | socat - /tmp/mpvsocket > /dev/null &'
				let prompt = "[mpv ipc] seek to " .  string(deduced_start_pos_secs)

				echo prompt
				call system(command)
				let sleeptime = float2nr(deduced_line_duration * 1000)
				exe 'sleep '. sleeptime . 'm'

				"silent execute "!".command
				redraw!
			endif
		endif
		let next_line_number = search('^EDL', 'nW')
	endwhile

	call tsv_edl#ipc_always_pause()
endfunction

let g:ipc_pause = v:true
"--------------------
"status line for vim-airline
"or raw status line
"--------------------
function! tsv_edl#status_line()
	if g:ipc_pause == v:true
		let pause_status = "■"
	else
		let pause_status = "▶"
	endif
	if g:ipc_media_ready
		let _status_line =  printf(pause_status .' '.  g:ipc_timecode .  " | " . g:ipc_loaded_media_name . " | /tmp/mpvsocket". ' ' )
	else
		"let g:airline_section_y='%{airline#util#wrap(airline#parts#ffenc(),0)}'
		let _status_line =  printf("< ")
	endif
	let _status_line = _status_line . g:cr_map_status 
	if g:cherry_pick_mode_entered
		"nothing to do
	endif
	return _status_line
endfunction

let g:airline_section_x='%{tsv_edl#status_line()}'
set statusline+=%{tsv_edl#status_line()}

"--------------------

let g:cherry_pick_mode_entered = v:false
let g:cr_map_status = "[⏎ = ⏎]"

function! tsv_edl#enter_cherry_pick_mode()
	if !g:cherry_pick_mode_entered
		tabnew
		tabmove 0
		set ft=tsv_edl
		noremap <silent> <cr> yy1gtGpg<tab>0cw---<ESC>0j
		let g:cr_map_status = "[⏎ = pick] "
		exe "normal! g\<Tab>"
		let g:cherry_pick_mode_entered = v:true
	else
		if !g:ipc_media_ready
			unmap <cr>
			let g:cr_map_status = "[⏎ = ⏎]"
		else
			noremap <silent> <cr> :call tsv_edl#ipc_seek()<CR>
			let g:cr_map_status = "[⏎ = seek] "
		endif
		let g:cherry_pick_mode_entered = v:false
	endif
endfunction

function! tsv_edl#enter_cherry_pick_mode_horizontally()
	if !g:cherry_pick_mode_entered
		"split selection.tsv
		new
		"move to bottom
		exe "normal! \<C-w>J"
		set ft=tsv_edl

		"switch back
		exe "normal! \<C-w>\<C-w>"
		noremap <silent> <cr> yy<C-w><C-w>Gp<C-W><C-w>0cw---<ESC>0j
		let g:cr_map_status = "[⏎ = pick] "
		let g:cherry_pick_mode_entered = v:true
	else
		if !g:ipc_media_ready
			unmap <cr>
			let g:cr_map_status = "[⏎ = ⏎]"
		else
			noremap <silent> <cr> :call tsv_edl#ipc_seek()<CR>
			let g:cr_map_status = "[⏎ = seek] "
		endif
		let g:cherry_pick_mode_entered = v:false
	endif
endfunction

function! tsv_edl#ipc_sync_playhead(backwards=v:false)
	let playback_time=tsv_edl#ipc_get_playback_time()
	let playback_time_in_timecode = tsv_edl#sec_to_timecode(str2float(playback_time))
	let g:ipc_timecode = "[" . playback_time_in_timecode . "]"
	echon "[mpv ipc] sync playhead to nearest " . g:ipc_timecode . ' '

	call cursor(0,1) " current line, first column

	" first search for \tHH:MM:SS,
	let _target = '\t' . playback_time_in_timecode[:7] .','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS-1,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time - 1))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS+1,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time + 1))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS-2,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time - 2))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS+2,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time + 2))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS-5,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time - 5))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS+5,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time + 5))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS-10,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time - 10))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS+10,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time + 10))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS-30,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time - 30))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" then search for \tHH:MM:SS+30,
	let _target = '\t' . tsv_edl#sec_to_timecode(str2float(playback_time + 30))[:7] . ','
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" if not found, then search for \tHH:MM:
	let _target = '\t' . playback_time_in_timecode[:5]
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif

	" FIXME use a while loop
	" then search for \tHH:
	let _target = '\t' . playback_time_in_timecode[:2]
	if s:search_target_and_go_to_that_line(_target, a:backwards) | return | endif
	echon "ipc_sync_playhead not found"

endfunction

function! s:line_clipname_match_mpc_filename(line_number)
	let line=getline(a:line_number)
	if len(line) > 0
		let line_list = split(line, '\t')
		if line_list[0] == 'EDL' || line_list[0] == '---' || line_list[0] == 'xxx'
			let filename = trim(trim(line_list[3],'|'))
			if filename ==# g:ipc_loaded_media_name
				"call cursor(_s, 1) " matched timecode line, first column
				return v:true
			endif
		endif
	endif
	return v:false
endfunction

function! s:search_target_and_go_to_that_line(_target, backwards=v:false)
	if a:backwards
		let _s = search(a:_target,'bncw')
	else
		let _s = search(a:_target,'ncw')
	endif
	if _s > 0
		if s:line_clipname_match_mpc_filename(_s)
			call cursor(_s, 1) " matched timecode line, first column
			return v:true
		endif
	endif
	return v:false
endfunction

function! tsv_edl#try_open_fold()
	try
		normal! zO
	catch /E490:/
		"no fold here
		"do nothing
	endtry
endfunction

function! tsv_edl#write_record_in()
	set conceallevel=0
	let playback_time=tsv_edl#ipc_get_playback_time()
	let rec_in = substitute(tsv_edl#sec_to_timecode(str2float(playback_time)), '\.', ',', '')
	if (getline(".")  !~# g:edl_line_pattern) "not a valid edl/---/xxx line
		"if len(getline(".")) != 0
		"	normal! o
		"endif
		call cursor(0,1)
		call setline(".", "EDL\t" . rec_in . "\t" . getline('.'))  "insert at head
		call cursor(0,col('$'))
	else  "overwrite
		call cursor(0,1) "this line head
		exec "normal! wcW" . rec_in
		echon "Overwrite record_in ... "
	endif

endfunction

function! tsv_edl#write_record_out()
	set conceallevel=0
	let playback_time=tsv_edl#ipc_get_playback_time()
	let rec_out = substitute(tsv_edl#sec_to_timecode(str2float(playback_time)), '\.', ',', '')

	let pattern_1 = "^EDL\\t\\d\\d:\\d\\d:\\d\\d,\\d\\d\\d\\t$"
	let pattern_2 = "^EDL\\t\\d\\d:\\d\\d:\\d\\d,\\d\\d\\d\\t\\d\\d:\\d\\d:\\d\\d,\\d\\d\\d"
	if (getline(".")  =~# pattern_1) " has a record_in
		call setline('.', getline('.') . rec_out . "\t" . '| ' . g:ipc_loaded_media_name . ' |' . "\t")
		let _rec_in_secs = tsv_edl#timecode_to_secs( substitute(split(getline('.'), '\t')[1], ',' , '.', 'g') )
		let line_duration = printf("%.2f", str2float(playback_time) - _rec_in_secs)
		call setline('.', getline('.') . line_duration . 's.')
	elseif (getline(".") =~# pattern_2) "full line overwrite
		echon "Overwrite record_out ... "
		exec "normal! 0WWcW" . rec_out
		let _rec_in_secs = tsv_edl#timecode_to_secs( substitute(split(getline('.'), '\t')[1], ',' , '.', 'g') )
		let line_duration = printf("%.2f", str2float(playback_time) - _rec_in_secs)
		call setline('.', getline('.') . ';' . line_duration . 's.')
	else
		call setline('.', getline('.') . rec_out . "\t" . '| ' . g:ipc_loaded_media_name . ' |' . "\t")
	endif
	call cursor(0,col('$'))
	startinsert!
endfunction

function! tsv_edl#ipc_get_playback_time()
	return trim(system('echo "{ \"command\": [\"get_property\", \"playback-time\" ] }" | socat - /tmp/mpvsocket 2>/dev/null | jq -r .data'))
endfunction
