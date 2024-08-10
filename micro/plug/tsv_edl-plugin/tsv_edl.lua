VERSION = "0.0.1"

local micro = import("micro")
local config = import("micro/config")
local buffer = import("micro/buffer")

local ipc_loaded_media_name = ""
local sleep = 0


function edl_break_line()
	local v = micro.CurPane()
	local cs = v.Buf:GetCursors()
	for i = 1, #cs do
		local c = cs[i]
		if c:HasSelection() then
			-- TODO: Do a multisplit and maintain the selection
		else
			line = v.Buf:Line(c.Y)
			lines = line_split(line, c.X)
			if lines then
				local a = buffer.Loc(0, c.Y)
				local b = buffer.Loc(c.X, c.Y)
			    v.Buf:Replace(buffer.Loc(0, c.Y), buffer.Loc(#line, c.Y), lines)
			end
		end
	end
end

-- Take one line and split it at X, returning two lines or nil
function line_split(line, X)
	local cursor_pos_percentage = infer_time_pos(line, X)
	if cursor_pos_percentage == nil then
		return nil
	end
	local record_in = line:sub(5,16)
	if record_in ~= string.match(record_in, "[0-9][0-9]:[0-9][0-9]:[0-9][0-9][,.][0-9][0-9][0-9]") then
		return nil
	end
	local record_out = line:sub(18,29)

	local start_secs = timecode_to_secs(record_in)
	local end_secs = timecode_to_secs(record_out)
	if cursor_pos_percentage <= 0 then return nil end
	local midpoint_secs = start_secs + ((end_secs - start_secs) * cursor_pos_percentage)
	local record_midpoint = secs_to_timecode(midpoint_secs)
	local edlpart = line:sub(1,3)
	local filepart = line:match("\t|[^|\t]*|\t")
	local text = line:match("[^\t]*$")
	local text_midpoint = text:len()*cursor_pos_percentage
	return string.format("%s\t%s\t%s%s%s\n%s\t%s\t%s%s%s",
		edlpart, record_in, record_midpoint, filepart, text:sub(1,text_midpoint),
		edlpart, record_midpoint, record_out, filepart, text:sub(text_midpoint+1))
end

function edl_join_selected_lines()
	local v = micro.CurPane()
	local cs = v.Buf:GetCursors()
	for i = 1, #cs do
		local c = cs[i]
		if c:HasSelection() then
			if c.CurSelection[1]:GreaterThan(-c.CurSelection[2]) then
				a, b = c.CurSelection[2], c.CurSelection[1]
			else
				a, b = c.CurSelection[1], c.CurSelection[2]
			end
			local line = lines_join(v.Buf, a.Y, b.Y)
			-- micro.Log(line)
			if line then
				v.Buf:Replace(buffer.Loc(0, a.Y), buffer.Loc(#v.Buf:Line(b.Y), b.Y), line)
			end
		else
			-- If there's no selection, don't do anything
		end
	end
end

-- Take multiple lines and turn them into one line.
function lines_join(buffer, a_Y, b_Y)
	local text = ""
	local firstline = buffer:Line(a_Y)
	local edlpart = firstline:sub(1,3)
	local record_in = firstline:sub(5,16)
	if record_in ~= string.match(record_in, "[0-9][0-9]:[0-9][0-9]:[0-9][0-9][,.][0-9][0-9][0-9]") then
		return nil
	end
	local record_out = record_in
	-- Iterate through the lines, checking the timestamps and concatenating text.
	local filepart = firstline:match("\t|[^|\t]*|\t")
	for i = a_Y, b_Y do
		local line = buffer:Line(i)
		if line:sub(5,16) ~= record_out then
			-- Each line must start where the previous line ended.
			return nil
		end
		if line:match("\t|[^|\t]*|\t") ~= filepart then
			-- Each line must have the same filepart
			return nil
		end
		record_out = line:sub(18,29)
		if text ~= "" then text = text .. " " end
		text = text .. line:match("[^\t]*$")
	end
	if record_out ~= string.match(record_out, "[0-9][0-9]:[0-9][0-9]:[0-9][0-9][,.][0-9][0-9][0-9]") then
		return nil
	end
	return string.format("%s\t%s\t%s%s%s",
		edlpart, record_in, record_out, filepart, text)
end

function edl_play_current_range()
	local v = micro.CurPane()
	local cs = v.Buf:GetCursors()
	if #cs ~= 1 then
		-- It doesn't make sense to use this with multicursors
		return
	end
	local length = ipc_seek(v.Buf:Line(cs[1].Y), cs[1].X)
	if length == 0 then
		return
	end
	ipc_always_play()
	ipc_sleep_pause(length)
end

function edl_toggle_play()
	is_playing = ipc_is_playing()
	if is_playing then
		ipc_always_pause()
		return
	end
	-- Otherwise, seek and start playing
	local v = micro.CurPane()
	local cs = v.Buf:GetCursors()
	if #cs ~= 1 then
		-- It doesn't make sense to use this with multicursors
		return
	end
	local length = ipc_seek(v.Buf:Line(cs[1].Y), cs[1].X)
	if length == 0 then
		-- Failed to seek, don't play.
		return
	end
	kill_pause_sleeper()
	ipc_always_play()
end

function ipc_init(filename)
	-- For some reason, the command to switch media doesn't work any more, so just kill it and restart it.
	local code = os.execute("pkill -f 'input-ipc-server=/tmp/mpvsocket' >/dev/null")
	os.execute('mpv --autofit-larger=90%x80% --ontop --no-terminal --keep-open=always --input-ipc-server=/tmp/mpvsocket --pause "' .. filename .. '" &')
	os.execute('sleep .2')
end


function ipc_always_play()
	os.execute('echo "{ \\"command\\": [\\"set_property\\", \\"pause\\", false ] }" | socat - /tmp/mpvsocket > /dev/null &')
end
function ipc_sleep_pause(time)
	kill_pause_sleeper()
	sleep = time
	os.execute('sleep "' .. time .. '" 2>/dev/null && echo "{ \\"command\\": [\\"set_property\\", \\"pause\\", true ] }" | socat - /tmp/mpvsocket > /dev/null &')
end
function kill_pause_sleeper()
	-- Note: this could be problematic if you have a lot of scripts that use 'sleep' in them.
	os.execute('pkill -xf "sleep ' .. sleep ..'"')
end
function ipc_always_pause()
	os.execute('echo "{ \\"command\\": [\\"set_property\\", \\"pause\\", true ] }" | socat - /tmp/mpvsocket > /dev/null &')
end
function ipc_is_playing()
	local pause_status=os_capture('echo "{ \\"command\\": [\\"get_property\\", \\"pause\\" ] }" | socat - /tmp/mpvsocket 2>/dev/null | jq -r .data | tr -d "\n"')
	if pause_status == "true" then
		return false
	elseif pause_status == "false" then
		return true
	end
	return nil
end

function ipc_load_media(filename, start)
	local filename_with_ext = filename
	if string.match(filename, "^http") == nil then
		filename_with_ext = os_capture('ls *"' .. filename .. '"* | ' .. " sed '/srt$/d; /tsv$/d; /txt$/d;' | head -n1 | tr -d '\n'")
	end
	ipc_init(filename_with_ext)
	-- micro.Log(filename_with_ext)
	ipc_loaded_media_name = filename
	return 0
end

-- Seek to the file at the position indicated by line, and
-- return the duration of the clip, or 0 if failed.
function ipc_seek(line, X)
	-- assume it's already loaded
	local type = line:sub(1,4)
	if type ~= "EDL\t" and type ~= "xxx\t" and type ~= '---\t' then
		-- TODO: move cursor to first EDL line?
		return 0
	end
	local record_in = line:sub(5,16):gsub(',','.')
	if record_in ~= string.match(record_in, "[0-9][0-9]:[0-9][0-9]:[0-9][0-9][,.][0-9][0-9][0-9]") then
		return 0
	end
	local record_out = line:sub(18,29)
	local filename = string.match(line:sub(31), "| *([^|\t]*[^ ]) *|\t")
	if filename == nil then
		return 0
	end

	local start_secs = timecode_to_secs(record_in)
	local _rec_out_secs = timecode_to_secs(record_out)
	-- start at cursor position
	local cursor_pos_percentage = infer_time_pos(line, X)
	if cursor_pos_percentage > 0 then
		start_secs = start_secs + ((_rec_out_secs - start_secs) * cursor_pos_percentage)
	end

	if filename ~= ipc_loaded_media_name then
		-- different media, load new.
		-- micro.Log(filename)
		ipc_load_media(filename, record_in)
	end

	os.execute('echo "{ \\"command\\": [\\"set_property\\", \\"playback-time\\", ' .. start_secs .. ' ] }" | socat - /tmp/mpvsocket > /dev/null &')
	return _rec_out_secs - start_secs
end

function os_capture(cmd, raw)
	local f = assert(io.popen(cmd, 'r'))
	local s = assert(f:read('*a'))
	f:close()
	return s
end

function infer_time_pos(line, X)
	local match = line:match("[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t")
	if match == nil then
		return nil
	end
	local non_text_len = match:len()
	if X < non_text_len then
		return 0
	end
	return (X - non_text_len) / (line:len() - non_text_len)
end

function timecode_to_secs(timecode)
	timecode = timecode:gsub(',','.')
	return timecode:sub(1,2)*3600 + timecode:sub(4,5)*60 + timecode:sub(7)
end
function secs_to_timecode(secs)
	return string.format("%02d:%02d:%06.3f", math.floor(secs/3600), math.floor(secs/60), secs%60)
end

function init()
	-- [mpv] play this line (guessing start pos at cursor), stop at end
	config.MakeCommand("edl_play_current_range", edl_play_current_range, config.NoComplete)
	config.MakeCommand("edl_toggle_play", edl_toggle_play, config.NoComplete)
	-- [split] this line into two, guessing a new timecode
	config.MakeCommand("edl_break_line", edl_break_line, config.NoComplete)
	config.MakeCommand("edl_join_selected_lines", edl_join_selected_lines, config.NoComplete)
end
