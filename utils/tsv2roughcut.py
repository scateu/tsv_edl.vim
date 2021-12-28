#!/usr/bin/env python3
import sys
import glob
import os.path
import subprocess
import tempfile

video_formats = ['mkv', 'mp4', 'mov', 'mpeg', 'ts', 'avi']
audio_formats = ['wav', 'mp3', 'm4a']

is_pure_audio_project = True

FPS = 24
RECORD_START_FROM_HOUR = 0  # or 1

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

output_queue = [] # [[filename, start_tc, end_tc], [...], [...], ...]

if __name__ == "__main__":
    counter = 0

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

    if is_pure_audio_project:
        with tempfile.TemporaryDirectory() as tempdirname:
            eprint("Open tempdir: ", tempdirname)
            counter = 0
            for f,r_in,r_out in output_queue:
                eprint("writing %05d.mp3"%counter)
                subprocess.call("ffmpeg -hide_banner -i \"%s\" -ss %s -to %s -c:a copy %s/%05d.mp3"%(f,r_in.replace(',','.'),r_out.replace(',','.'),tempdirname,counter), shell=True)
                counter += 1

            with open("%s/selection.txt"%tempdirname,"w") as output_file:
                for i in range(len(output_queue)):
                    output_file.write("file '%s/%05d.mp3'\n"%(tempdirname,i))

            eprint("writing selection.mp3")
            subprocess.call("ffmpeg -hide_banner -safe 0 -f concat -i %s/selection.txt -c copy selection.mp3"%tempdirname, shell=True)
    else:
        with tempfile.TemporaryDirectory() as tempdirname:
            eprint("Open tempdir: ", tempdirname)
            for f,r_in,r_out in output_queue:
                eprint("writing %05d.mkv"%counter)
                subprocess.call("ffmpeg -hide_banner -i \"%s\" -ss %s -to %s -c:a copy %s/%05d.mkv"%(f,r_in.replace(',','.'),r_out.replace(',','.'),tempdirname,counter), shell=True)
                counter += 1

            with open("%s/selection.txt"%tempdirname,"w") as output_file:
                for i in range(len(output_queue)):
                    output_file.write("file '%s/%05d.mkv'\n"%(tempdirname,i))

            eprint("writing selection.mkv")
            subprocess.call("ffmpeg -hide_banner -safe 0 -f concat -i %s/selection.txt -c copy selection.mkv"%tempdirname, shell=True)
