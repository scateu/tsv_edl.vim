#!/usr/bin/env python3
import sys
import glob
import os
import subprocess
import tempfile
import platform

video_formats = ['mkv', 'mp4', 'mov', 'mpeg', 'ts', 'avi']
audio_formats = ['wav', 'mp3', 'm4a']

is_pure_audio_project = True

GENERATE_SRT = True
FPS = 24
FCPX_SCALE=90000 #number = sec * 90000

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def srttime_to_sec(srttime):
    assert(srttime.count(":") == 2)
    assert(srttime.count(",") == 1)
    HH, MM, SS, MS = [int(d) for d in srttime.replace(",",":").split(":")]
    return HH*3600 + MM*60 + SS + MS/1000.0

def srttime_to_fcpx_int(srttime, FPS=FPS, fcp_scale=FCPX_SCALE):
    assert(srttime.count(":") == 2)
    assert(srttime.count(",") == 1)
    h,m,s,ms = [int(d) for d in srttime.replace(",",":").split(":")]
    ms_scaled = int(ms/1000.0 * FPS) * (fcp_scale / FPS)  #frames * 3750/FCPX_SCALE * FCPX_SCALE
    return h*3600*fcp_scale + m*60*fcp_scale + s*fcp_scale + ms_scaled

def fcpx_int_to_srttime(number, fcp_scale=FCPX_SCALE):
    return sec_to_srttime(number / FCPX_SCALE)

def sec_to_srttime(sec):
    HH = int(sec/3600.0)
    MM = int((sec - 3600.0*HH)/60.0)
    SS = int(sec - HH*3600.0 - MM*60.0)
    MS = (sec - int(sec))*1000.0
    return "%02d:%02d:%02d,%03d"%(HH,MM,SS,MS)

def stitch_edl_queue(raw_queue):
    length = len(raw_queue)
    stitched_output = [] 
    i = 0
    while i < length:
        clip, t1, t2 = raw_queue[i]
        j = i + 1
        if (i == length - 1): #last line
            stitched_output.append(raw_queue[i])
            break
        clip_next, t1_next, t2_next = raw_queue[j]
        _item = [clip, t1, t2]
        while (clip == clip_next and t2 == t1_next):
            _item = [clip, t1, t2_next] #update pending output
            clip, t1, t2 = _item #update item on the left to be examined
            j += 1
            if (j == length): #out of index
                break
            clip_next, t1_next, t2_next = raw_queue[j]
        stitched_output.append(_item)
        i = j
    return stitched_output

output_queue = [] # [[filename, start_tc, end_tc], [...], [...], ...]

srt_queue = []

if __name__ == "__main__":
    srt_counter = 1
    #srt_last_position = 0.0 #in sec
    srt_last_position_in_fcpx_int = 0 # sec/90000

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

    while True: # read EDL lines
        line = sys.stdin.readline()
        if not line:
            sys.stdin.close()
            break

        if line.startswith('EDL'):
            _l = line.strip()
            if _l.count('|'):
                clipname = _l.split('|')[1].strip()
                _l = _l.split('|')[0]
                #import pdb;pdb.set_trace()
            else:
                continue
            _l = _l.split() #['EDL', '01:26:16.12', '01:27:22.10']
            record_in = _l[1]
            record_out  = _l[2]

            if GENERATE_SRT:
                # FIXME: when pure audio project. don't use FCPX int
                #t2 = srttime_to_sec(record_out)
                t2 = srttime_to_fcpx_int(record_out)
                #t1 = srttime_to_sec(record_in)
                t1 = srttime_to_fcpx_int(record_in)
                srt_duration_in_fcpx_int = t2 - t1
                #eprint("srt_duration:", srt_duration)
                if not ('[ SPACE' in line):
                    _s = line.strip().split('\t')
                    if len(_s) > 4: #subtitle is not empty
                        if srt_counter != 0: #not first block
                            srt_queue.append("")
                        srt_queue.append("%d"%srt_counter)
                        srt_queue.append("%s --> %s"%(fcpx_int_to_srttime(srt_last_position_in_fcpx_int), fcpx_int_to_srttime(srt_last_position_in_fcpx_int + srt_duration_in_fcpx_int))) 
                        # FIXME: accumulatived error. may have something to do with varied FPS
                        # FIXME: may utilize ffmpeg, treat srt as a stream as well.
                        # FIXME: ffmpeg -i input.mp4 -sub_charenc ISO-8859-1 -i input.srt -map 0:v -map 0:a -c copy -map 1 -c:s:0 mov_text output.mp4
                        # FIXME: https://superuser.com/questions/1433644/ffmpeg-unable-to-recode-subtitle-event
                        srt_queue.append( _s[4].replace("\\N",'\n') )
                        srt_counter += 1
                srt_last_position_in_fcpx_int += srt_duration_in_fcpx_int

            filenames_v = [ c for c in glob.glob("*%s*"%clipname) if os.path.splitext(c)[1][1:].lower() in video_formats ]
            filenames_a = [ c for c in glob.glob("*%s*"%clipname) if os.path.splitext(c)[1][1:].lower() in audio_formats ]

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
                    eprint("WARNING: NO clip similar to \"%s\" found. Skip."%clipname)
                    continue
            output_queue.append([filename, record_in, record_out])

    if len(output_queue) > 99999:
        eprint("Too much. That's too much.")
        sys.exit(-1)

    # stitch adjecent clips in output_queue
    before_stitch_lines = len(output_queue)
    output_queue = stitch_edl_queue(output_queue)
    after_stitch_lines = len(output_queue)
    eprint("[stitch] %d --> %d lines"%(before_stitch_lines, after_stitch_lines))

    if is_pure_audio_project: #Audio only
        with tempfile.TemporaryDirectory() as tempdirname:
            eprint("[tempdir]", tempdirname)
            counter = 0
            eprint("[ffmpeg] writing ", end="") 
            for f,r_in,r_out in output_queue:
                eprint("%05d.mp3 "%counter, end="")
                sys.stderr.flush()
                subprocess.call("ffmpeg -hide_banner -loglevel error -i \"%s\" -ss %s -to %s -c:a copy %s/%05d.mp3"%(f,r_in.replace(',','.'),r_out.replace(',','.'),tempdirname,counter), shell=True)
                counter += 1
            eprint("")

            with open("%s/roughcut.txt"%tempdirname,"w") as output_file:
                for i in range(len(output_queue)):
                    output_file.write("file '%s/%05d.mp3'\n"%(tempdirname,i))

            roughcut_ext_name = ".mp3" # or ".mkv"
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
            eprint("[ffmpeg concat] writing",roughcut_filename)

            if GENERATE_SRT:
                eprint("[srt] writing",srt_filename)
                with open(srt_filename, "w") as output_file:
                    output_file.write('\n'.join(srt_queue))

            subprocess.call("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt -c copy %s"%(tempdirname, roughcut_filename), shell=True)
    else: # VIDEEEEO
        with tempfile.TemporaryDirectory() as tempdirname:
            eprint("[tempdir]", tempdirname)
            counter = 0
            eprint("[ffmpeg] writing ", end="") 
            for f,r_in,r_out in output_queue:
                eprint(" %05d.ts"%counter, end="")
                sys.stderr.flush()
                if 0: # it worked.
                    #FIXME detect if it's macOS. otherwise libx264
                    subprocess.call("ffmpeg -hide_banner -loglevel error -i \"%s\" -ss %s -to %s -c:v %s -b:v 2M -c:a copy %s/%05d.ts"%(f, r_in.replace(',','.'), r_out.replace(',','.'), codec_v ,tempdirname,counter), shell=True)

                if 1: # but this works faster in seeking
                    #a = r_in.replace(',',':').split(':')
                    t1 = srttime_to_fcpx_int(r_in) / FCPX_SCALE  #115.3
                    #t1 = int(a[0])*3600 + int(a[1])*60 + int(a[2]) #+ int(a[3])/1000.0
                    skip_time = 15
                    if (t1 - skip_time > 0):
                        t2 = int(t1) - skip_time  #100
                        t3 = skip_time + t1 - int(t1) #15+115.3-115 = 15.3
                    else:
                        t2 = 0
                        t3 = t1

                    b = r_out.replace(',',':').split(':')

                    if 1:
                        #eprint("fps=24, scale=1920:1080")
                        # use -to to get more accuracy
                        to = srttime_to_fcpx_int(r_out) / FCPX_SCALE - t2
                        subprocess.call("ffmpeg -hide_banner -loglevel error -ss %s -i \"%s\" -ss %s -to %s -vf 'fps=%d, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M %s/%05d.ts"%(t2, f, t3, to, FPS, codec_v, tempdirname,counter), shell=True)
                        # Dropframe causes more inaccuracy to srt than round( floatNumber, 3)
                        # a FPS filter is very good.
                        # -r? no good.
                    else:
                        duration = (int(b[0])*3600 + int(b[1])*60 + int(b[2]) + int(b[3])/1000.0) - (int(a[0])*3600 + int(a[1])*60 + int(a[2]) + int(a[3])/1000.0) 
                        subprocess.call("ffmpeg -hide_banner -loglevel error -ss %s -i \"%s\" -ss %s -t %s -c:v %s -b:v 2M %s/%05d.ts"%(t2, f, t3, duration, codec_v,tempdirname,counter), shell=True)

                if 0:
                    a = r_in.replace(',',':').split(':')
                    t1 = int(a[0])*3600 + int(a[1])*60 + int(a[2]) + int(a[3])/1000.0
                    b = r_out.replace(',',':').split(':')
                    t2 = int(b[0])*3600 + int(b[1])*60 + int(b[2]) + int(b[3])/1000.0
                    subprocess.call("ffmpeg -hide_banner -loglevel error -i \"%s\" -vf \"trim=start=%s:end=%s,setpts=PTS-STARTPTS\" -af \"atrim=start=%s:end=%s,asetpts=PTS-STARTPTS\" -c:v %s  %s/%05d.ts"%(f, t1, t2, t1, t2, codec_v, tempdirname,counter), shell=True)
                # NOTE -ss -to placed before -i, cannot be used with -c copy
                # See https://trac.ffmpeg.org/wiki/Seeking
                counter += 1
            eprint("") # .ts segments written

            with open("%s/roughcut.txt"%tempdirname,"w") as output_file:
                for i in range(len(output_queue)):
                    output_file.write("file '%s/%05d.ts'\n"%(tempdirname,i))

            roughcut_ext_name = ".mp4" # or ".mkv"
            roughcut_filename = "roughcut" + roughcut_ext_name
            srt_filename = "roughcut.srt"
            if os.path.exists("roughcut"+roughcut_ext_name):
                rename_counter = 1
                roughcut_filename = "roughcut_1"+roughcut_ext_name
                srt_filename = "roughcut_1.srt"
                while os.path.exists(roughcut_filename):
                    rename_counter += 1
                    roughcut_filename = "roughcut_%d"%rename_counter + roughcut_ext_name
                    srt_filename = "roughcut_%d.srt"%rename_counter
            eprint("[ffmpeg concat] writing",roughcut_filename)

            if GENERATE_SRT:
                eprint("[srt] writing ",srt_filename)
                with open(srt_filename, "w") as output_file:
                    output_file.write('\n'.join(srt_queue))

            subprocess.call("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt -c:v copy %s"%(tempdirname, roughcut_filename), shell=True)

    if len(sys.argv) > 1: #wait for user input then rename
        if "--user-input-newname" in sys.argv:
            sys.stdin = os.fdopen(1)

            newname = input("Input CLIPNAME to rename. ENTER to ignore > ")
            newname = newname.strip()
            if len(newname) == 0:
                eprint("ignored. keeping name [%s] [%s]"%(roughcut_filename, srt_filename))
                sys.exit(0)
        else:
            newname = sys.argv[1]
        eprint("[Rename] ", roughcut_filename, 'to', '[' + newname + roughcut_ext_name + ']')
        os.rename(roughcut_filename, newname + roughcut_ext_name)
        eprint("[Rename] ", srt_filename, 'to', '[' + newname + '.srt' + ']')
        os.rename(srt_filename, newname + '.srt')
