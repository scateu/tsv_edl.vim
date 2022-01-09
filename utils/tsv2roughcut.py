#!/usr/bin/env python3
import sys
import glob
import os.path
import subprocess
import tempfile

video_formats = ['mkv', 'mp4', 'mov', 'mpeg', 'ts', 'avi']
audio_formats = ['wav', 'mp3', 'm4a']

is_pure_audio_project = True

GENERATE_SRT = True

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

output_queue = [] # [[filename, start_tc, end_tc], [...], [...], ...]

srt_queue = []

if __name__ == "__main__":
    srt_counter = 0
    srt_last_position = 0.0 #in sec
    while True:
        line = sys.stdin.readline()
        if not line:
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
                t2 = srttime_to_sec(record_out)
                t1 = srttime_to_sec(record_in)
                srt_duration = round(t2 - t1, 3)
                #eprint("srt_duration:", srt_duration)
                if not ('[ SPACE' in line):
                    if srt_counter != 0: #not first block
                        srt_queue.append("")
                    srt_queue.append("%d"%srt_counter)
                    srt_queue.append("%s --> %s"%(sec_to_srttime(srt_last_position), sec_to_srttime( round(srt_last_position + srt_duration,3) ) ) )
                    # FIXME: accumulatived error. may have something to do with varied FPS
                    # FIXME: may utilize ffmpeg, treat srt as a stream as well.
                    srt_queue.append(line.strip().split('\t')[4].replace("\\N",'\n'))
                    srt_counter += 1
                srt_last_position += srt_duration
                srt_last_position = round(srt_last_position, 3)

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

    if is_pure_audio_project: #Audio only
        with tempfile.TemporaryDirectory() as tempdirname:
            eprint("Open tempdir: ", tempdirname)
            counter = 0
            for f,r_in,r_out in output_queue:
                eprint("[ffmpeg] writing %05d.mp3"%counter)
                subprocess.call("ffmpeg -hide_banner -loglevel error -i \"%s\" -ss %s -to %s -c:a copy %s/%05d.mp3"%(f,r_in.replace(',','.'),r_out.replace(',','.'),tempdirname,counter), shell=True)
                counter += 1

            with open("%s/roughcut.txt"%tempdirname,"w") as output_file:
                for i in range(len(output_queue)):
                    output_file.write("file '%s/%05d.mp3'\n"%(tempdirname,i))

            roughcut_filename = "roughcut.mp3"
            srt_filename = "roughcut.srt"
            if os.path.exists("roughcut.mp3"):
                rename_counter = 1
                roughcut_filename = "roughcut_1.mp3"
                srt_filename = "roughcut_1.srt"
                while os.path.exists(roughcut_filename):
                    rename_counter += 1
                    roughcut_filename = "roughcut_%d.mp3"%rename_counter
                    srt_filename = "roughcut_%d.srt"%rename_counter
            eprint("[ffmpeg concat] writing ",roughcut_filename)

            if GENERATE_SRT:
                eprint("[srt] writing ",srt_filename)
                with open(srt_filename, "w") as output_file:
                    output_file.write('\n'.join(srt_queue))

            subprocess.call("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt -c copy %s"%(tempdirname, roughcut_filename), shell=True)
    else: # VIDEEEEO
        with tempfile.TemporaryDirectory() as tempdirname:
            eprint("Open tempdir: ", tempdirname)
            counter = 0
            for f,r_in,r_out in output_queue:
                eprint("[ffmpeg] writing %05d.ts"%counter)
                if 0: # it worked.
                    #FIXME detect if it's macOS. otherwise libx264
                    subprocess.call("ffmpeg -hide_banner -loglevel error -i \"%s\" -ss %s -to %s -c:v h264_videotoolbox -b:v 2M -c:a copy %s/%05d.ts"%(f, r_in.replace(',','.'), r_out.replace(',','.'), tempdirname,counter), shell=True)

                if 1: # but this works faster in seeking
                    a = r_in.replace(',',':').split(':')
                    t1 = int(a[0])*3600 + int(a[1])*60 + int(a[2]) #+ int(a[3])/1000.0
                    skip_time = 15
                    if (t1 - skip_time > 0):
                        t2 = t1 - skip_time
                        t3 = skip_time + int(a[3])/1000.0
                    else:
                        t2 = 0
                        t3 = t1 + int(a[3])/1000.0

                    b = r_out.replace(',',':').split(':')

                    if 1:
                        #eprint("fps=24, scale=1920:1080")
                        # use -to to get more accuracy
                        to = round(srttime_to_sec(r_out) - t2, 3)
                        subprocess.call("ffmpeg -hide_banner -loglevel error -ss %s -i \"%s\" -ss %s -to %s -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v h264_videotoolbox -b:v 2M %s/%05d.ts"%(t2, f, t3, to, tempdirname,counter), shell=True)
                        # Dropframe causes more inaccuracy to srt than round( floatNumber, 3)
                        # a FPS filter is very good.
                        # -r? no good.
                    else:
                        duration = (int(b[0])*3600 + int(b[1])*60 + int(b[2]) + int(b[3])/1000.0) - (int(a[0])*3600 + int(a[1])*60 + int(a[2]) + int(a[3])/1000.0) 
                        subprocess.call("ffmpeg -hide_banner -loglevel error -ss %s -i \"%s\" -ss %s -t %s -c:v h264_videotoolbox -b:v 2M %s/%05d.ts"%(t2, f, t3, duration, tempdirname,counter), shell=True)

                if 0:
                    a = r_in.replace(',',':').split(':')
                    t1 = int(a[0])*3600 + int(a[1])*60 + int(a[2]) + int(a[3])/1000.0
                    b = r_out.replace(',',':').split(':')
                    t2 = int(b[0])*3600 + int(b[1])*60 + int(b[2]) + int(b[3])/1000.0
                    subprocess.call("ffmpeg -hide_banner -loglevel error -i \"%s\" -vf \"trim=start=%s:end=%s,setpts=PTS-STARTPTS\" -af \"atrim=start=%s:end=%s,asetpts=PTS-STARTPTS\" -c:v h264_videotoolbox  %s/%05d.ts"%(f, t1, t2, t1, t2, tempdirname,counter), shell=True)
                # NOTE -ss -to placed before -i, cannot be used with -c copy
                # See https://trac.ffmpeg.org/wiki/Seeking
                counter += 1

            with open("%s/roughcut.txt"%tempdirname,"w") as output_file:
                for i in range(len(output_queue)):
                    output_file.write("file '%s/%05d.ts'\n"%(tempdirname,i))

            roughcut_output_type = ".mp4" # or ".mkv"
            roughcut_filename = "roughcut" + roughcut_output_type
            srt_filename = "roughcut.srt"
            if os.path.exists("roughcut"+roughcut_output_type):
                rename_counter = 1
                roughcut_filename = "roughcut_1"+roughcut_output_type
                srt_filename = "roughcut_1.srt"
                while os.path.exists(roughcut_filename):
                    rename_counter += 1
                    roughcut_filename = "roughcut_%d"%rename_counter + roughcut_output_type
                    srt_filename = "roughcut_%d.srt"%rename_counter
            eprint("[ffmpeg concat] writing",roughcut_filename)

            if GENERATE_SRT:
                eprint("[srt] writing ",srt_filename)
                with open(srt_filename, "w") as output_file:
                    output_file.write('\n'.join(srt_queue))

            subprocess.call("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt -c copy %s"%(tempdirname, roughcut_filename), shell=True)
