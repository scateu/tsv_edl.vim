VERSION = "0.0.0"

local micro = import("micro")
local config = import("micro/config")
local buffer = import("micro/buffer")

local ipc_loaded_media_name = ""


function edl_break_line()
	local v = micro.CurPane()
	local cs = v.Buf:GetCursors()
	for i = 1, #cs do
		local c = cs[i]
		if c:HasSelection() then
			-- continue
			-- TODO: do multiple splits when something is selected
		else
			-- c.Loc
		end
		-- TODO: do the thing
	end
end

function edl_play_current_range()
	local v = micro.CurPane()
	local cs = v.Buf:GetCursors()
	if #cs ~= 1 then
		-- It doesn't make sense to use this with multicursors
		return
	end
	if ipc_seek(v.Buf:Line(cs[1].Y)) == 0 then
		return
	end
	ipc_always_play()
end

function ipc_always_play()
	os.execute('echo "{ \\"command\\": [\\"set_property\\", \\"pause\\", false ] }" >> /tmp/mpvsocket &')
end
function ipc_always_pause()
	os.execute('echo "{ \\"command\\": [\\"set_property\\", \\"pause\\", true ] }" >> /tmp/mpvsocket &')
end

function ipc_load_media(filename)
	local filename_with_ext = filename
	if string.match(filename, "^http") == nil then
		filename_with_ext = os_capture('ls *"' .. filename .. '"* | ' .. " sed '/srt$/d; /tsv$/d; /txt$/d;' | head -n1 | tr -d '\n'")
	end
	os.execute('echo "{ \\"command\\": [\\"loadfile\\", \\"' .. filename_with_ext .. '\\", \\"replace\\", \\"start=' .. 0 .. '\\" ] }" >> /tmp/mpvsocket &')
	ipc_loaded_media_name = filename
	return 0
end

function ipc_seek(line)
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
	local record_out = line:sub(18,29):gsub(',','.')
	local filename = string.match(line:sub(31), "| *([^|\t]*[^ ]) *|\t")
	if filename == nil then
		return 0
	end
	if filename ~= ipc_loaded_media_name then
		-- different media, load new.
		ipc_load_media(filename)
	end

	-- TODO: start at cursor position?
	-- let cursor_pos_percentage = tsv_edl#infer_time_pos(line)
	local _rec_in_secs = timecode_to_secs(record_in)
	local _rec_out_secs = timecode_to_secs(record_out)

	os.execute('echo "{ \\"command\\": [\\"set_property\\", \\"playback-time\\", ' .. _rec_in_secs .. ' ] }" >> /tmp/mpvsocket &')
end

function os_capture(cmd, raw)
	local f = assert(io.popen(cmd, 'r'))
	local s = assert(f:read('*a'))
	f:close()
	return s
end

function timecode_to_secs(timecode)
	return timecode:sub(1,2)*3600 + timecode:sub(4,5)*60 + timecode:sub(7)
end

function init()
	-- [mpv] play this line (guessing start pos at cursor), stop at end
	config.MakeCommand("edl_play_current_range", edl_play_current_range, config.NoComplete)
	-- [split] this line into two, guessing a new timecode
	config.MakeCommand("edl_break_line", edl_break_line, config.NoComplete)
end
