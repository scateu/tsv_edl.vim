VERSION = "0.0.0"

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

function line_split(line, X)
	local cursor_pos_percentage = infer_time_pos(line, X)
	local record_in = line:sub(5,16)
	if record_in ~= string.match(record_in, "[0-9][0-9]:[0-9][0-9]:[0-9][0-9][,.][0-9][0-9][0-9]") then
		return nil
	end
	local record_out = line:sub(18,29)

	local start_secs = timecode_to_secs(record_in)
	local end_secs = timecode_to_secs(record_out)
	if cursor_pos_percentage <= 0 then return nil end
	local midpoint_secs = start_secs + ((end_secs - start_secs) * cursor_pos_percentage)
	record_midpoint = secs_to_timecode(midpoint_secs)
	edlpart = line:sub(1,3)
	filepart = line:match("\t|[^|\t]*|\t")
	text = line:match("[^\t]*$")
	text_midpoint = text:len()*cursor_pos_percentage
	return string.format("%s\t%s\t%s%s%s\n%s\t%s\t%s%s%s",
		edlpart, record_in, record_midpoint, filepart, text:sub(1,text_midpoint),
		edlpart, record_midpoint, record_out, filepart, text:sub(text_midpoint+1))
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
	if is_playing == nil then return end
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
	local code = os.execute("pgrep -f 'input-ipc-server=/tmp/mpvsocket' >/dev/null")
	if code == 1 then
		os.execute('mpv --autofit-larger=90%x80% --ontop --no-terminal --keep-open=always --input-ipc-server=/tmp/mpvsocket --no-focus-on-open --pause "' .. filename .. '" &')
		os.execute('sleep .2')
	end
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
	os.execute('echo "{ \\"command\\": [\\"loadfile\\", \\"' .. filename_with_ext .. '\\", \\"replace\\", \\"start=' .. start .. '\\" ] }" | socat - /tmp/mpvsocket > /dev/null &')
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
	local non_text_len = line:match("[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t"):len()
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
end
