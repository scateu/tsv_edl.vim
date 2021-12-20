#!/usr/bin/env python3
import sys

#TODO: 把RECORD_START_FROM_HOUR和FPS作为argparse暴露出来

FPS = 24
DEFAULT_CLIPNAME = "multicam" #以英文为好，Davinci里中文有可能识别不出来
RECORD_START_FROM_HOUR = 0  # or 1

'''
Usage:

    grep EDL Selection.org  | python3 tsv2edl.py  > Selection.edl

EDL 01:26:16.12 01:27:22.10 | Cam A
EDL 01:26:16.12 01:27:22.10 | Cam A | comments, yadayadayada
EDL 01:15:29 01:17:14
EDL 0:53:52.29 0:54:37.36
EDL 00:01:44:12 00:01:44:23

导两遍，一遍关联到带SRT的timeline上，用于切字幕
另一遍关联到Multicam上。

## 如何在vim里Cherrypick
   EDL Cherrypick in Vim

    vim -o a.tsv b.tsv
    :nmap <cr> yy<C-W>wGp<C-w>w0cw---<ESC>0j
    然后在一行上回车，复制本行到另一个窗口，然后回来把EDL标为---以示用过

### tab风格的操作
    vim -p selection.tsv a.tsv b.tsv c.tsv
    :nmap <cr> yy1gtGpg<tab>0cw---<ESC>0j
    :nmap <space> 1gtG2o<esc>g<tab>

### 配置好之后 :mksession
    :mksession edit.vim
    $ vim -S edit.vim

    也可以不加名字
    :mksession
    $ vim -S

### 配色

:highlight Assertions ctermfg=gray guifg=gray
:2match Assertions /^---.*$/
:set cursorline 

### Conceal

:syntax match Normal '\d\d:\d\d.*|\t' conceal
:set concealcursor=nvic

'''

def convert_srt_time_to_EDL_time(srt_time, shift_hour = 0):
    srt_time = srt_time.strip()
    if srt_time.count(":") == 2 and srt_time.count(".") == 0 and srt_time.count(",") == 0 :
       #01:26:16
       h,m,s = [int(data) for data in srt_time.replace(".",":").split(":")]
       ms = 0
    elif srt_time.count(":") == 2 and srt_time.count(".") == 1 and srt_time.count(",") == 0:
       #0:53:52.29
       h,m,s,ms = [int(data) for data in srt_time.replace(".",":").split(":")]
       ms *= 10
    elif srt_time.count(":") == 2 and srt_time.count(",") == 1 and srt_time.count(".") == 0: # 00:01:44,416
       h,m,s,ms = [int(data) for data in srt_time.replace(",",":").split(":")]
    elif srt_time.count(":") == 3 and srt_time.count(",") == 0 and srt_time.count(".") == 0: # 00:01:44:12
       return srt_time
    else:
        raise Exception('Invalid timecode: %s'%srt_time)
    return "%02d:%02d:%02d:%02d"%(h + shift_hour, m, s, int(ms*FPS/1000))

def EDL_time_add(t1, t2):
   h1,m1,s1,f1 = [int(d) for d in t1.split(":")]
   h2,m2,s2,f2 = [int(d) for d in t2.split(":")]
   assert(f1<FPS)
   assert(f2<FPS)
   assert(s1<60)
   assert(s2<60)
   assert(m1<60)
   assert(m2<60)

   carrybit = 0
   f = f1 + f2
   if f >= FPS:
       f %= FPS
       carrybit = 1

   s = s1 + s2 + carrybit
   carrybit = 0
   if s >= 60:
       s %= 60
       carrybit = 1

   m = m1 + m2 + carrybit
   carrybit = 0
   if m >= 60:
       m %= 60
       carrybit = 1

   h = h1 + h2 + carrybit
   carrybit = 0
   
   return "%02d:%02d:%02d:%02d"%(h,m,s,f)

def EDL_time_minus(t2, t1):
   h2,m2,s2,f2 = [int(d) for d in t2.split(":")]
   h1,m1,s1,f1 = [int(d) for d in t1.split(":")]

   frames = h2*60*60*FPS + m2*60*FPS + s2*FPS + f2 - (h1*60*60*FPS + m1*60*FPS + s1*FPS + f1)
   assert(frames > 0)
   h = int(frames / (60*60*FPS))
   m = int((frames - h*60*60*FPS)/(60*FPS))
   s = int((frames - h*60*60*FPS - m*60*FPS)/FPS)
   f = frames - h*60*60*FPS - m*60*FPS - s*FPS
   return "%02d:%02d:%02d:%02d"%(h,m,s,f)


if __name__ == "__main__":
    last_edl_position = "01:00:00:00"

    counter = 0

    print("TITLE: Awesome Project 1")
    print("FCM: NON-DROP FRAME")
    print("")

    edl_sentence = """{counter}  AX       V     C        {record_in} {record_out} {program_in} {program_out}
* FROM CLIP NAME: {clipname} 

{counter}  AX       A     C        {record_in} {record_out} {program_in} {program_out}
* FROM CLIP NAME: {clipname}
"""
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        clipname = DEFAULT_CLIPNAME # default

        if line.startswith('EDL'):
            _l = line.strip()
            if _l.count('|'):
                clipname = _l.split('|')[1]
                _l = _l.split('|')[0]
                #import pdb;pdb.set_trace()
            _l = _l.split() #['EDL', '01:26:16.12', '01:27:22.10']
            record_in = convert_srt_time_to_EDL_time(_l[1], shift_hour=RECORD_START_FROM_HOUR)
            record_out  = convert_srt_time_to_EDL_time(_l[2], shift_hour=RECORD_START_FROM_HOUR)
            program_in = last_edl_position
            program_out = EDL_time_add(program_in, EDL_time_minus(record_out, record_in))
            last_edl_position = program_out
            counter += 1
            print(edl_sentence.format(counter="%03d"%counter,
                record_in = record_in,
                record_out = record_out,
                program_in = program_in,
                program_out = program_out,
                clipname = clipname))


"""
TODO: Marker

EDLMarker 01:15:29


TITLE: marker
FCM: NON-DROP FRAME

001  001      V     C        01:00:10:11 01:00:10:12 01:00:10:11 01:00:10:12
 |C:ResolveColorBlue |M:Marker 1 |D:1

002  001      V     C        01:00:20:07 01:00:20:08 01:00:20:07 01:00:20:08
 |C:ResolveColorRed |M:Marker 2 haha |D:1

003  001      V     C        01:00:32:11 01:00:32:12 01:00:32:11 01:00:32:12
 |C:ResolveColorMint |M:测试 |D:1

"""

