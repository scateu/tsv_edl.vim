#!/usr/bin/env python3
import sys
import glob
import os
import subprocess
import tempfile
import platform
import argparse

video_formats = ['mkv', 'mp4', 'mov', 'mpeg', 'ts', 'avi', 'webm']
audio_formats = ['wav', 'mp3', 'm4a', 'ogg']
image_formats = ['png', 'jpg', 'jpeg', 'bmp']

is_pure_audio_project = True

GENERATE_SRT = True

DEBUG = False

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def srttime_to_sec(srttime):
    assert(srttime.count(":") == 2)
    assert(srttime.count(",") == 1)
    HH, MM, SS, MS = [int(d) for d in srttime.replace(",",":").split(":")]
    return HH*3600 + MM*60 + SS + MS/1000.0

def sec_to_srttime(sec):
    HH = int(sec/3600.0)
    MM = int((sec - 3600.0*HH)/60.0)
    SS = int(sec - HH*3600.0 - MM*60.0)
    MS = (sec - int(sec))*1000.0
    return "%02d:%02d:%02d,%03d"%(HH,MM,SS,MS)


def is_b_roll_continuous(first, second):
    # B roll has padding by 1/24.0 to prevent ffmpeg leak one frame of A clip.
    if first != "NO_B_ROLL" and second != "NO_B_ROLL":
        #if first[0] == second[0] and first[2] == second[1]: #filename, out = in
        if first[0] == second[0] and abs(second[1] - first[2]) < 2/24.0 : #filename, out = in
            return True
    elif first == "NO_B_ROLL" and second == "NO_B_ROLL":
        return True
    else:
        return False

def join_b_roll(first, second):
    if first != "NO_B_ROLL" and second != "NO_B_ROLL":
        #assert(first[2] == second[1])
        assert(abs(first[2] - second[1]) < 2/24.0)
        assert(first[0] == second[0])
        return [first[0], first[1], second[2]]
    if first == "NO_B_ROLL" and second == "NO_B_ROLL":
        return "NO_B_ROLL"

def stitch_edl_queue(raw_queue):
    # [ filename, in, out, NO_B_ROLL]
    # [ filename, in, out, [filename, in, out]]
    length = len(raw_queue)
    stitched_output = []
    i = 0
    while i < length:
        clip, t1, t2, b_roll = raw_queue[i]
        j = i + 1
        if (i == length - 1): #last line
            stitched_output.append(raw_queue[i])
            break
        clip_next, t1_next, t2_next, b_roll_next = raw_queue[j]
        _item = [clip, t1, t2, b_roll]
        while (clip == clip_next and t2 == t1_next and is_b_roll_continuous(b_roll, b_roll_next)):
            _item = [clip, t1, t2_next, join_b_roll(b_roll, b_roll_next)] #update pending output
            clip, t1, t2, b_roll = _item #update item on the left to be examined
            j += 1
            if (j == length): #out of index
                break
            clip_next, t1_next, t2_next, b_roll_next = raw_queue[j]
        stitched_output.append(_item)
        i = j
    return stitched_output

def accurate_and_fast_time_for_ffmpeg(r_in,r_out, skip_time=15):
    # r_in, r_out are in secs
    a = r_in
    b = r_out
    t1 = int(a)
    if (t1 - skip_time > 0):
        t2 = t1 - skip_time
        t3 = skip_time + (a - t1)
    else:
        t2 = 0
        t3 = t1 + (a - t1)
    to = round(b - t2, 3)
    duration = b-a
    return t2,t3,to,duration

def determine_filename_from_clipname(clipname):
    global is_pure_audio_project  #as long as one clip has video, this project goes videeeeeo!
    filenames_v = [ c for c in glob.glob("*%s*.*"%clipname) if os.path.splitext(c)[1][1:].lower() in video_formats ]
    #FIXME didn't test. *%s*.*
    filenames_a = [ c for c in glob.glob("*%s*.*"%clipname) if os.path.splitext(c)[1][1:].lower() in audio_formats ]
    # FIXME a.mp3 another.m4a
    filenames_i = [ c for c in glob.glob("*%s*"%clipname) if os.path.splitext(c)[1][1:].lower() in image_formats ]

    if len(filenames_v) > 1:
        eprint("WARNING: filename similar to clip %s has more than one"%clipname)
        eprint("Choosing the %s"%filenames_v[0])
        filename = filenames_v[0]
        is_pure_audio_project = False
    elif len(filenames_v) == 1:
        filename = filenames_v[0]
        is_pure_audio_project = False
    elif len(filenames_v) == 0:
        if len(filenames_a) > 1:
            eprint("WARNING: filenames similar to clip %s has more than one"%clipname)
            eprint("Choosing the %s"%filenames_v[0])
            filename = filenames_a[0]
        elif len(filenames_a) == 1:
            filename = filenames_a[0]
        elif len(filenames_a) == 0:
            if len(filenames_i) > 1: # 5. No Video, no audio. Multiple still image matched.
                is_pure_audio_project = False
                eprint("WARNING: filenames similar to clip %s has more than one"%clipname)
                eprint("Choosing the %s"%filenames_i[0])
                filename = filenames_i[0]
            elif len(filenames_i) == 1: # 6. No Video, no audio. one still image
                is_pure_audio_project = False
                filename = filenames_i[0]
            elif len(filenames_i) == 0: # 7. No, no, no. Nothing.
                eprint("WARNING: NO clip similar to \"%s\" found. Skip."%clipname)
                filename = ""
    return filename

def handle_bilibili_clip(url, r_in, r_out, f_B, counter, tempdirname):
    txt_lines = []
    fragment_ext = "ts"   #ts will make A-V sync better
    stream_urls = subprocess.check_output( ['yt-dlp', '-g', url], encoding='UTF-8').splitlines() # -f "w*" #select worst format for bilibili. FIXME
    assert(len(stream_urls) == 2)

    t2, t3, to, duration = accurate_and_fast_time_for_ffmpeg(r_in, r_out)

    command = "ffmpeg -hide_banner -loglevel error -user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.106 Safari/537.36\" -headers \"Referer: %s\" -ss %s -i \"%s\" -ss %s -t %s %s/%05d_0.mp4"%(url, t2, stream_urls[0], t3, duration, tempdirname, counter)
    # bilibili doesn't allow 2 downloader running simultaneously
    # youtube-dl --dump-user-agent
    # [BiliBili] Format(s) 720P 高清, 1080P 高码率, 1080P 高清 are missing; you have to login or become premium member to download them
    eprint(".",end=""); sys.stderr.flush()
    if DEBUG:
        eprint("")
        eprint("[yt-dlp:bilibili] "+command)
    subprocess.call(command, shell=True)

    command = "ffmpeg -hide_banner -loglevel error -user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.106 Safari/537.36\" -headers \"Referer: %s\" -ss %s -i \"%s\" -ss %s -t %s %s/%05d_1.mp4"%(url, t2, stream_urls[1], t3, duration, tempdirname, counter)
    eprint(".",end=""); sys.stderr.flush()
    if DEBUG:
        eprint("[yt-dlp:bilibili] "+command)
    subprocess.call(command, shell=True)

    command = "ffmpeg -hide_banner -loglevel error -i %s/%05d_0.mp4 -i %s/%05d_1.mp4 -qscale 0 %s/%05d.%s"%(tempdirname, counter, tempdirname, counter, tempdirname, counter, fragment_ext)
    eprint(".",end=""); sys.stderr.flush()
    if DEBUG:
        eprint("[yt-dlp:bilibili] "+command)
    subprocess.call(command, shell=True)
    handle_b_roll(f_B, tempdirname, counter, fragment_ext, codec_v, "")
    return "file '%s/%05d.%s'"%(tempdirname,counter,fragment_ext)

def handle_http_clip(url, r_in, r_out, f_B, counter, tempdirname): #youtube, twitter
    #FIXME seeking needs the same strategy
    t1 = r_in
    t2 = r_out
    fragment_ext = "mp4"
    #command = "yt-dlp --download-sections \"*%.2f-%.2f\" %s -o %s/%05d --recode-video mp4"%(t1, t2, url, tempdirname, counter )
    #--merge-output-format mkv
    # this command doesn't work very well, causing A-V sync and stall issues
    command = "ffmpeg -hide_banner -loglevel error -user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.106 Safari/537.36\" -headers \"Referer: %s\" $(yt-dlp -g %s | sed \"s/.*/-ss %s -i &/\") -t %s %s/%05d.%s"%(url, url, t1, t2-t1, tempdirname, counter, fragment_ext)
    # https://www.reddit.com/r/youtubedl/comments/rx4ylp/ytdlp_downloading_a_section_of_video/
    # courtesy of user18298375298759
    eprint(".",end=""); sys.stderr.flush()
    if DEBUG:
        eprint("")
        eprint("[yt-dlp] "+command)
    subprocess.call(command, shell=True)
    #command2 = "ffmpeg -i %s/%05d.mkv %s/%05d.ts"%(tempdirname, counter, tempdirname, counter)
    #eprint("[ffmpeg] "+command2)
    #subprocess.call(command2, shell=True)
    #fragment_ext = "ts"
    handle_b_roll(f_B, tempdirname, counter, fragment_ext, codec_v, "")
    return "file '%s/%05d.%s'"%(tempdirname,counter,fragment_ext)

def handle_local_clip(f, r_in, r_out, f_B, counter, tempdirname):
    # in a video project
    fragment_ext = "ts"

    t2, t3, to, duration = accurate_and_fast_time_for_ffmpeg(r_in, r_out)
    #eprint("fps=24, scale=1920:1080")
    # use -to to get more accuracy
    ext = os.path.splitext(f)[1].lower()[1:]
    if ext in video_formats:
        subprocess.call("ffmpeg -hide_banner -loglevel error -ss %s -i \"%s\" -ss %s -to %s -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M %s/%05d.ts"%(t2, f, t3, to, codec_v, tempdirname,counter), shell=True)
        # Dropframe causes more inaccuracy to srt than round( floatNumber, 3)
        # a FPS filter is very good.
        # -r? no good.
    elif ext in audio_formats:  #audio clip in a video project. generate a black screen
        subprocess.call("ffmpeg -hide_banner -loglevel error -f lavfi -i color=size=1920x1080:rate=24:color=black -ss %s -i \"%s\" -ss %s -to %s -c:v %s -b:v 2M -shortest %s/%05d.ts"%(t2, f, t3, to, codec_v, tempdirname,counter), shell=True)
    else: #still image
        subprocess.call("ffmpeg -hide_banner -loglevel error -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -loop 1 -i \"%s\" -t %s -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M -shortest %s/%05d.ts"%(f, to-t3, codec_v, tempdirname,counter), shell=True)

    handle_b_roll(f_B, tempdirname, counter, fragment_ext, codec_v, "")

    # NOTE -ss -to placed before -i, cannot be used with -c copy
    # See https://trac.ffmpeg.org/wiki/Seeking
    return "file '%s/%05d.%s'\n"%(tempdirname,counter,fragment_ext)

def handle_b_roll(f_B, tempdirname, counter, extname, codec_v, codec_a):
    if f_B == "NO_B_ROLL":
        return
    #Has B Roll
    ts_filename = "%s/%05d.%s"%(tempdirname, counter, extname)
    _ts_filename = "%s/_%05d.%s"%(tempdirname, counter, extname)
    http_ts_filename = "%s/http_%05d.%s"%(tempdirname, counter, extname)
    b_ts_filename = "%s/b_%05d.%s"%(tempdirname, counter, extname)

    assert(len(f_B) == 3)
    b_filename, b_in, b_out = f_B
    subprocess.call("mv %s %s"%(ts_filename,_ts_filename), shell=True)  #rename from 00000.ts to _00000.ts

    if b_filename.lower().startswith("http"):
        if b_filename.find("bilibili.com") != -1: #bilibili
            handle_bilibili_clip(b_filename, b_in, b_out, "NO_B_ROLL", counter, tempdirname)  #no c roll actually
            # TODO scale to 1080p, otherwise, place on center
        else:  #youtube, twitter, ...
            handle_http_clip(b_filename, b_in, b_out, "NO_B_ROLL", counter, tempdirname)
        subprocess.call("mv %s %s"%(ts_filename,http_ts_filename), shell=True)  #rename from 00000.ts to http_00000.ts
        subprocess.call("ffmpeg -hide_banner -loglevel error -i %s -i %s -filter_complex \"[1:v]setpts=PTS, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[a]; [0:v][a]overlay=eof_action=pass[vout]; [0][1] amix [aout]\" -map [vout] -map [aout] -c:v %s -shortest -b:v 2M %s"%(_ts_filename, http_ts_filename, codec_v, ts_filename), shell=True)
    else:  # local file as B roll
        b_t2,b_t3,b_to, b_duration = accurate_and_fast_time_for_ffmpeg(b_in,b_out)

        # Render b_00000.ts:
        ext = os.path.splitext(b_filename)[1].lower()[1:]
        if ext in video_formats:
            subprocess.call("ffmpeg -hide_banner -loglevel error -ss %s -i \"%s\" -ss %s -to %s -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M %s"%(b_t2, b_filename, b_t3, b_to, codec_v, b_ts_filename), shell=True)
            # then overlay b_00000.ts / _00000.ts --> 00000.ts
            subprocess.call("ffmpeg -hide_banner -loglevel error -i %s -i %s -filter_complex \"[1:v]setpts=PTS[a]; [0:v][a]overlay=eof_action=pass[vout]; [0][1] amix [aout]\" -map [vout] -map [aout] -c:v %s -shortest -b:v 2M %s"%(_ts_filename, b_ts_filename, codec_v, ts_filename), shell=True)
            # Apply the following filter to the bg video: tpad=stop=-1:stop_mode=clone and use eof_action=endall in overlay.
            #https://stackoverflow.com/questions/73504860/end-the-video-when-the-overlay-video-is-finished
        elif ext in audio_formats: # B roll is pure audio
            subprocess.call("ffmpeg -hide_banner -loglevel error -ss %s -to %s -i \"%s\" -i %s -filter_complex \"[0][1] amix [aout]\" -map 1:v -map [aout] -c:v %s -shortest %s"%(b_t2+b_t3, b_t2+b_to, b_filename, _ts_filename, "copy", ts_filename), shell=True)
            # accurate_and_fast_time_for_ffmpeg seeking doesn't work with multiple input.
        else: #still image
            #subprocess.call("ffmpeg -hide_banner -loglevel error -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -loop 1 -i \"%s\" -t %s -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M -shortest %s/b_%05d.ts"%(b_filename, b_to-b_t3, codec_v, tempdirname,counter), shell=True)
            subprocess.call("ffmpeg -hide_banner -loglevel error -i %s -loop 1 -t %s -i \"%s\" -filter_complex \"[1:v]fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[a]; [0:v][a]overlay=eof_action=pass[vout]\" -map [vout] -map a:0 -c:v %s -b:v 2M %s"%(_ts_filename, b_to-b_t3, b_filename, codec_v, ts_filename), shell=True)
    eprint("+",end="") #indicates B roll generated

def handle_audio_clip(f, r_in, r_out, f_B, counter, tempdirname, intermediate_ext_name):
    if intermediate_ext_name == None:
        audioclips_ext_name = os.path.splitext(f)[1].lower()
        intermediate_audio_codec = '-c:a copy'
    else:
        audioclips_ext_name = intermediate_ext_name
        intermediate_audio_codec = ''
    eprint("%05d%s "%(counter,audioclips_ext_name), end="")
    sys.stderr.flush()

    ############ FAST and ACCURE SEEKING  #########
    t2, t3, to, duration = accurate_and_fast_time_for_ffmpeg(r_in, r_out)

    subprocess.call("ffmpeg -hide_banner -loglevel error -ss %s -i \"%s\" -ss %s -t %s %s %s/%05d%s"%(t2,f,t3,duration, intermediate_audio_codec, tempdirname,counter, audioclips_ext_name), shell=True)
    return "file '%s/%05d%s'"%(tempdirname, counter, audioclips_ext_name)

def determine_output_audio_file_ext(output_queue):
    exts = list(set([os.path.splitext(c[0])[1][1:].lower() for c in output_queue]))
    if exts == ['wav']:
        roughcut_ext_name = '.wav'
        roughcut_audio_codec = '-c:a copy'
        intermediate_ext_name = None
    elif exts == ['mp3']:
        roughcut_ext_name = '.mp3'
        roughcut_audio_codec = '-c:a copy'
        intermediate_ext_name = None
    elif exts == ['m4a']:
        roughcut_ext_name = '.m4a'
        roughcut_audio_codec = '-c:a copy'
        intermediate_ext_name = None
    else:
        intermediate_ext_name = ".wav"
        roughcut_ext_name = ".mp3" # or ".mkv"
        roughcut_audio_codec = '-c:a libmp3lame -b:a 320k'
        #roughcut_audio_codec = ''
    return roughcut_ext_name, roughcut_audio_codec, intermediate_ext_name

def determine_roughcut_filename(roughcut_ext_name):
    roughcut_filename = "roughcut" + roughcut_ext_name
    srt_filename = "roughcut.srt"
    if os.path.exists(roughcut_filename):
        rename_counter = 1
        roughcut_filename = "roughcut_1" + roughcut_ext_name
        srt_filename = "roughcut_1.srt"
        while os.path.exists(roughcut_filename):
            rename_counter += 1
            roughcut_filename = "roughcut_%d"%rename_counter + roughcut_ext_name
            srt_filename = "roughcut_%d.srt"%rename_counter
    return roughcut_filename, srt_filename


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("outfile", nargs='?', help="file name for output")
    parser.add_argument("-u", "--user-input-newname", action="store_true", help="wait for user input then rename")
    parser.add_argument("-p", "--play", action="store_true", help="play after generated")
    parser.add_argument("-k", "--ask-before-delete-temp-files", action="store_true", help="ask before delete temp files")
    args = parser.parse_args()

    output_queue = [] # [[filename, start_tc in secs, end_tc in secs], [...], [...], ...]
    B_buffer = [] # [filename, start_tc, end_tc]
    srt_queue = []
    srt_counter = 1
    srt_last_position = 0.0 #in sec

    #$ printf("\e[?1004l")
    # https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
    # otherwise, annoying ^[[O ^[[I will appear when terminal focus lost or get again.
    print("\033[?1004l", end="")
    sys.stdout.flush()

    if platform.system() == "Darwin":
        codec_v = "h264_videotoolbox"
    elif platform.system() == "Linux":
        codec_v = "libx264"
    else:
        codec_v = "libx264"

######### 1. eat lines into output_queue
    while True: # read EDL lines
        line = sys.stdin.readline()
        if not line:
            sys.stdin.close()
            break

        if line.startswith('EDL'):
            _l = line.strip()
            if _l.count('|'):
                _l, clipname, subtitle = [item.strip() for item in _l.split('|')]
                #import pdb;pdb.set_trace()
            else:
                continue
            _l = _l.split() #['EDL', '01:26:16.12', '01:27:22.10']
            record_in = _l[1].replace('"', '')  #Number.app will add quote to time code as "01:02:03,123"
            record_out  = _l[2].replace('"', '')

            if GENERATE_SRT:
                t2 = srttime_to_sec(record_out)
                t1 = srttime_to_sec(record_in)
                srt_duration = round(t2 - t1, 3)
                #eprint("srt_duration:", srt_duration)
                if not ('[ SPACE' in line or '|\t[B]' in line):
                    _s = line.strip().split('\t')
                    if len(_s) > 4: #subtitle is not empty
                        if srt_counter != 0: #not first block
                            srt_queue.append("")
                        srt_queue.append("%d"%srt_counter)
                        srt_queue.append("%s --> %s"%(sec_to_srttime(srt_last_position), sec_to_srttime( round(srt_last_position + srt_duration,3) ) ) )
                        # FIXME: accumulatived error. may have something to do with varied FPS
                        # FIXME: may utilize ffmpeg, treat srt as a stream as well.
                        # FIXME: ffmpeg -i input.mp4 -sub_charenc ISO-8859-1 -i input.srt -map 0:v -map 0:a -c copy -map 1 -c:s:0 mov_text output.mp4
                        # FIXME: https://superuser.com/questions/1433644/ffmpeg-unable-to-recode-subtitle-event
                        srt_queue.append( _s[4].replace("\\N",'\n') )
                        srt_counter += 1
                if '|\t[B]' in line:
                    pass  #B roll shouldn't increase srt time.
                else:
                    srt_last_position += srt_duration
                    srt_last_position = round(srt_last_position, 3)

            if clipname.startswith("http"):
                is_pure_audio_project = False
                #filename = list(filter(None, clipname.split('/')))[-1] + ".mp4"
                filename = clipname
            else:
                filename = determine_filename_from_clipname(clipname)
                if filename == "": #not found
                    continue

            if subtitle.startswith("[B]"): #B-roll, EDL 00:00:00,000    00:00:01,000    | somevideo |   [B] b-roll
                B_buffer = [filename, srttime_to_sec(record_in), srttime_to_sec(record_out)]
            else: #Normal lines
                output_queue.append([filename, srttime_to_sec(record_in), srttime_to_sec(record_out), "B_ROLL_UNDETERMINED"])

                if isinstance(B_buffer, list) and len(B_buffer) == 3: #handle B roll buffer
                    f_a,s_a,e_a = output_queue[-1][:3] #A: filename, start, end
                    f_b,s_b,e_b = B_buffer  #B: filename, start, end
                    # B roll shorter than A clip
                    duration_a = e_a - s_a
                    duration_b = e_b - s_b
                    if duration_b <= duration_a:
                        output_queue[-1][3]=B_buffer  # [f,in,out, B_ROLL]
                        B_buffer = "" #clear B_buffer
                    else:
                        # B roll longer than A clip
                        # B.start = A.end; next
                        output_queue[-1][3] = [f_b, s_b,  s_b + duration_a + 1.0/24.0]  # [f,in,out, B_ROLL]
                        # make sure B roll covers the end of A clip. Padding one frame for B roll. don't worry, the next start timecode isn't affected.
                        B_buffer = [f_b, s_b + duration_a , e_b]
                        # MAYBE DONE: B Roll may be cut into pieces. Due to uncompleted stitching of A clips.
                        #       Maybe stitching B roll afterwards is a good idea.  Maybe I was overthinking....  Wed Mar 15 00:30:35 CST 2023
                        # B: [..................]
                        # A: [.....||.......||.....
                else:
                    output_queue[-1][3]="NO_B_ROLL"  #[f,in,out,"NO_B_ROLL"]

    #print(output_queue);import sys;sys.exit(-1)

######### 2. stitch lines

    if len(output_queue) > 99999:
        eprint("Too much. That's too much.")
        sys.exit(-1)

    # stitch adjecent clips in output_queue
    before_stitch_lines = len(output_queue)
    output_queue = stitch_edl_queue(output_queue)
    eprint("[stitch] %d --> %d lines"%(before_stitch_lines, len(output_queue)))

######### 3. clip by clip generating
########## 3.1 pure audio project
    if is_pure_audio_project: #Audio only
        roughcut_ext_name, roughcut_audio_codec, intermediate_ext_name =  determine_output_audio_file_ext(output_queue)
        with tempfile.TemporaryDirectory() as tempdirname:
            eprint("[tempdir]", tempdirname)
            counter = 0
            eprint("[ffmpeg] writing ", end="")
            with open("%s/roughcut.txt"%tempdirname,"w") as output_file:
                for f,r_in,r_out, f_B in output_queue:
                    output_file.write(handle_audio_clip(f, r_in, r_out, f_B, counter, tempdirname, intermediate_ext_name))
                    output_file.write('\r\n')
                    counter += 1
                eprint("")

            roughcut_filename, srt_filename = determine_roughcut_filename(roughcut_ext_name)
            eprint("[ffmpeg concat] writing",roughcut_filename)

            if GENERATE_SRT:
                eprint("[srt] writing",srt_filename)
                with open(srt_filename, "w") as output_file:
                    output_file.write('\n'.join(srt_queue))
            subprocess.call("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt %s %s"%(tempdirname, roughcut_audio_codec, roughcut_filename), shell=True)

            try:  # in Shortcuts.app  OSError: [Errno 9] Bad file descriptor
                sys.stdin = os.fdopen(1)
                if args.ask_before_delete_temp_files:
                    input("Press enter to destory temp dir:  %s  > "%tempdirname)
            except OSError:
                pass
########## 3.2 video project
    else: # VIDEEEEO
        roughcut_txt_lines = [] #to generate roughcut.txt
        with tempfile.TemporaryDirectory() as tempdirname:
            eprint("[tempdir]", tempdirname)
            counter = 0
            eprint("[ffmpeg] writing ", end="")
            #eprint(output_queue)
            for f,r_in,r_out,f_B in output_queue:
                eprint(" %05d"%counter, end="")
                sys.stderr.flush()
                if f.startswith('http'):
                    #00:02:03,500 -> 123.5
                    if f.find("bilibili.com") != -1: #bilibili
                        roughcut_txt_lines.append(handle_bilibili_clip(f, r_in, r_out, f_B, counter, tempdirname))
                    else:  #youtube, twitter, ...
                        roughcut_txt_lines.append(handle_http_clip(f, r_in, r_out, f_B, counter, tempdirname))
                else: #local media files
                    roughcut_txt_lines.append(handle_local_clip(f, r_in, r_out, f_B, counter, tempdirname))
                counter += 1
            eprint("") # .ts segments written

            ##### GENERATE roughcut.txt #####
            with open("%s/roughcut.txt"%tempdirname,"w") as output_file:
                output_file.write("\n".join(roughcut_txt_lines))

            ############# Determine srt_filename, roughcut_filename for final combining in step 4 ####################
            roughcut_ext_name = ".mp4" # or ".mkv"
            roughcut_filename, srt_filename = determine_roughcut_filename(roughcut_ext_name)
            eprint("[ffmpeg concat] writing",roughcut_filename)

            if GENERATE_SRT:
                eprint("[srt] writing ",srt_filename)
                with open(srt_filename, "w") as output_file:
                    output_file.write('\n'.join(srt_queue))

            #subprocess.call("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt -c copy %s"%(tempdirname, roughcut_filename), shell=True)
            # To make preview in macOS work, re-encode audio. Hope it won't bring to much pain.
            subprocess.call("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt -ss 0 -c:v copy %s"%(tempdirname, roughcut_filename), shell=True)

            # > '-ss', '0', // If we don't do this, the output seems to start with an empty black after merging with the encoded part
            # tips from losslesscut project.

            try:  # in Shortcuts.app  OSError: [Errno 9] Bad file descriptor
                sys.stdin = os.fdopen(1)
                if args.ask_before_delete_temp_files:
                    input("Press enter to destory temp dir:  %s  > "%tempdirname)
            except OSError:
                pass

######### 4. combine into one
    # roughcut_filename, srt_filename is determined.
    filename_change_needed = False
    if args.user_input_newname:
        newname = input("Input CLIPNAME to rename. ENTER to ignore > ").strip()
        filename_change_needed = True
        if len(newname) == 0:
            eprint("ignored. keeping name [%s] [%s]"%(roughcut_filename, srt_filename))
            filename_change_needed = False
    else: #expect a user name from args.outfile
        if args.outfile:  # has a positional file name given by user.
            newname = args.outfile
            filename_change_needed = True
        else:  #use roughcut_x.xxx
            pass
    if filename_change_needed:
        eprint("[Rename] ", roughcut_filename, 'to', '[' + newname + roughcut_ext_name + ']')
        os.rename(roughcut_filename, newname + roughcut_ext_name)
        roughcut_filename = newname + roughcut_ext_name  #for play
        eprint("[Rename] ", srt_filename, 'to', '[' + newname + '.srt' + ']')
        os.rename(srt_filename, newname + '.srt')
        srt_filename = newname + '.srt'  #for play
    else:
        eprint("{filename} & {filename_srt} generated".format(filename=roughcut_filename, filename_srt=srt_filename))

    if args.play:
        subprocess.call("mpv \"{filename}\"".format(filename=roughcut_filename), shell=True)
        #FIXME: tsv2roughcut  缺最后一行的回车，可能会导致srt2tsv脚本失效

