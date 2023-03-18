#!/usr/bin/env python3
#-*- coding:utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import urllib.parse
import os
import glob
import sys
import argparse
import math

FCPX_SCALE = 90000 * 4
#FPS = 24
video_formats = ['mkv', 'mp4', 'mov', 'mpeg', 'ts', 'avi']
audio_formats = ['wav', 'mp3', 'm4a']
image_formats = ['png', 'jpg', 'jpeg', 'bmp']

is_pure_audio = True

xmlheader1 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.8">
    <resources>
        <format id="r1" frameDuration="{fps}/{fcpx_scale}s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>"""
# 24 FPS: 3750/90000
# 25 FPS: 3600/90000
# 23.976 FPS: 3753.75/90000 = 15015/360000

xmlheader2 = """
        <asset id="{ref_id}" src="file://{mediapath}" start="0s" duration="{duration}s" hasVideo="{hasVideo}" hasAudio="{hasAudio}" format="r1" audioSources="1" audioChannels="1" audioRate="48000" />"""
#FIXME 36000s for 10hour max. Davinci Resolve will ignore source tape after 10hour; FCPX doesn't care


xmlheader3 = """
    </resources>
    <library>
        <event name="DEFAULT">
            <project name="DEFAULT">
                <sequence format="r1" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
                    <spine>"""

#TODO: 用模板语言?

xmltail = """                    </spine>
                </sequence>
            </project>
        </event>
    </library>
</fcpxml>"""

"""
         |     s     |  gap    | s_next    |
       start        end

<asset-clip name="MyMovie3" ref="r2" offset="5s" start="15s" duration="5s" audioRole="dialogue" />
"""

def timecode_to_fcpx_time(timecode, FPS, fcpx_scale=FCPX_SCALE):
    timecode = timecode.strip().replace(",", ":")
    h,m,s,ms = [int(d) for d in timecode.split(":")]
    ms_scaled = ms/1000.0 * fcpx_scale
    return round(h*3600*fcpx_scale + m*60*fcpx_scale + s*fcpx_scale + ms_scaled)

def timecode_to_frame_number(timecode, FPS):
    timecode = timecode.strip().replace(",", ":")
    h,m,s,ms = [int(d) for d in timecode.split(":")]
    return round(h*3600*FPS + m*60*FPS + s*FPS + ms/1000.0 * FPS)

def sec_to_srttime(sec):
    HH = int(sec/3600.0)
    MM = int((sec - 3600.0*HH)/60.0)
    SS = int(sec - HH*3600.0 - MM*60.0)
    MS = (sec - int(sec))*1000.0
    return "%02d:%02d:%02d,%03d"%(HH,MM,SS,MS)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def stitch_fcpxml_queue(raw_queue):
    #([clipname, ref_id, offset, fcpx_record_in, duration, lane ])
    length = len(raw_queue)
    stitched_output = []
    i = 0
    while i < length:
        clip, r, o, t1, d, lane, subtitle = raw_queue[i]
        j = i + 1
        if (i == length - 1): #last line
            stitched_output.append(raw_queue[i])
            break
        clip_next, r_next, o_next, t1_next, d_next, lane_next, subtitle_next = raw_queue[j]
        output_pending = [clip, r, o, t1, d, lane, subtitle]
        while (clip == clip_next and r == r_next and t1 + d == t1_next and lane == lane_next):
            output_pending = [clip, r, o, t1, d + d_next, lane, subtitle + '\n' + subtitle_next] #update pending output
            #update item on the left to be examined
            [clip, r, o, t1, d, lane, subtitle] = output_pending
            j += 1
            if (j == length): #out of index
                break
            clip_next, r_next, o_next, t1_next, d_next, lane_next, subtitle_next = raw_queue[j]
        stitched_output.append(output_pending)
        i = j
    return stitched_output

def find_b_roll_of_clip(offset_A, duration_A, output_queue_B):
    # if output_queue_B item's offset is within [offset, offset + duration] of output_queue, then output as nested.
    indexs = []
    index = -1
    for clipname_B, ref_id_B, offset_B, fcpx_record_in_B, duration_B, lane_B, subtitle_B in output_queue_B:
        index += 1
        if offset_A <= offset_B < (offset_A + duration_A):
            indexs.append(index)
        if (offset_B+duration_B) >= (offset_A+duration_A):
            eprint("WARNING: B roll reaches the outside of A roll")
    return indexs

def determine_filename_from_clipname(clipname):
    filenames_v = [ c for c in glob.glob("*%s*"%clipname) if os.path.splitext(c)[1][1:].lower() in video_formats ]
    filenames_a = [ c for c in glob.glob("*%s*"%clipname) if os.path.splitext(c)[1][1:].lower() in audio_formats ]
    filenames_i = [ c for c in glob.glob("*%s*"%clipname) if os.path.splitext(c)[1][1:].lower() in image_formats ]
    isStillPicture = 0
    if len(filenames_v) > 1:  # 1. Multiple Video Footage
        eprint("WARNING: filename similar to clip %s has more than one"%clipname)
        eprint("Choosing the %s"%filenames_v[0])
        filename = filenames_v[0]
        is_pure_audio = False
        abspath = os.path.abspath(filename)
        hasVideo = 1
        hasAudio = 1
        media_duration = 36000
        isStillPicture = 0
    elif len(filenames_v) == 1:  # 2. Only one video footage matched.
        filename = filenames_v[0]
        is_pure_audio = False
        abspath = os.path.abspath(filename)
        hasVideo = 1
        hasAudio = 1
        media_duration = 36000
        isStillPicture = 0
    elif len(filenames_v) == 0:
        if len(filenames_a) > 1:  # 3. No video matched. Multiple audio matched
            eprint("WARNING: filenames similar to clip %s has more than one"%clipname)
            eprint("Choosing the %s"%filenames_a[0])
            filename = filenames_a[0]
            is_pure_audio = True
            abspath = os.path.abspath(filename)
            hasVideo = 0
            hasAudio = 1
            media_duration = 36000
            isStillPicture = 0
        elif len(filenames_a) == 1: # 4. No video matched. Only one audio matched.
            filename = filenames_a[0]
            is_pure_audio = True
            abspath = os.path.abspath(filename)
            hasVideo = 0
            hasAudio = 1
            media_duration = 36000
            isStillPicture = 0
        elif len(filenames_a) == 0:
            if len(filenames_i) > 1: # 5. No Video, no audio. Multiple still image matched.
                eprint("WARNING: filenames similar to clip %s has more than one"%clipname)
                eprint("Choosing the %s"%filenames_i[0])
                filename = filenames_i[0]
                is_pure_audio = False  #is_pure_audio is deprecated. FIXME
                abspath = os.path.abspath(filename)
                hasVideo = 1
                hasAudio = 0
                media_duration = 0
                isStillPicture = 1
            elif len(filenames_i) == 1: # 6. No Video, no audio. one still image
                filename = filenames_i[0]
                abspath = os.path.abspath(filename)
                hasVideo = 1
                hasAudio = 0
                media_duration = 0
                isStillPicture = 1
            elif len(filenames_i) == 0: # 7. No, no, no. Nothing.
                hasVideo = 1
                hasAudio = 1
                media_duration = 36000
                eprint("WARNING: NO clip similar to \"%s\" found. Skip."%clipname)
                abspath = clipname
                isStillPicture = 0
                #continue
    return filename, abspath, hasVideo, hasAudio, media_duration, isStillPicture

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='convert tsv_edl to fcpxml')
    parser.add_argument('--offsetonehour', action="store_true", default=False)
    parser.add_argument('--fps', action="store", default=25, type=float)
    parser.add_argument('--nosrt', action="store_false", default=True)
    arguments = parser.parse_args()

    GENERATE_SRT = arguments.nosrt
    OFFSET_1HOUR = arguments.offsetonehour
    FPS = arguments.fps

    media_assets = {} # { "clipname": [ abspath, ref_id, hasVideo, hasAudio, media_duration, isStillPicture ] , ... }
    xmlhead = ""
    xmlbody = ""
    output_queue = []
    output_queue_B = []
    xmlhead += xmlheader1.format(fps=int(FCPX_SCALE/FPS), fcpx_scale = FCPX_SCALE)
    #xmlhead += xmlheader1.format(fps=3753.75)
    offset = 0
    eprint("Be advised: %.3fFPS, 48000Hz."%(FPS))
    if OFFSET_1HOUR:
        eprint("OFFSET_1HOUR: TIMECODE shifted by 1 hour, making DaVinci Resolve happy.")
        eprint("TIPS: to paste one whole timeline on top of another, you may need to uncheck auto-track-selector in DaVinci Resolve.")
    srt_queue = []
    srt_counter = 1
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        if line.startswith('EDL'):
            _l = line.strip()
            if _l.count('|'):
                _items = _l.split('|')
                clipname = _items[1].strip()
                filename, abspath, hasVideo, hasAudio, media_duration, isStillPicture = determine_filename_from_clipname(clipname)

                if not clipname in media_assets:
                    ref_id = "r%d"%(len(media_assets) + 2) #id start from r2
                    media_assets[clipname] = [abspath, ref_id, hasVideo, hasAudio, media_duration, isStillPicture ]
                else:
                    ref_id = media_assets[clipname][1]

                _r = _items[0].split() #['EDL', '01:26:16.12', '01:27:22.10']
                #fcpx_record_in = timecode_to_fcpx_time(_r[1], FPS)
                #fcpx_record_out  = timecode_to_fcpx_time(_r[2], FPS)
                _r[1] = _r[1].replace('"', '')
                _r[2] = _r[2].replace('"', '')
                fcpx_record_in = round(timecode_to_frame_number(_r[1], FPS) * FCPX_SCALE / FPS)
                fcpx_record_out  = round(timecode_to_frame_number(_r[2], FPS) * FCPX_SCALE / FPS)
                duration = fcpx_record_out - fcpx_record_in

                if OFFSET_1HOUR: #shift all timecode by 1hour, to make Davinci Resolve's default behavior happy
                    fcpx_record_in += 3600 * FCPX_SCALE
                    fcpx_record_out += 3600 * FCPX_SCALE

                if fcpx_record_out == fcpx_record_in: #FIXME
                    fcpx_record_out += FCPX_SCALE / FPS

                if GENERATE_SRT:
                    subtitle = _items[2].strip()
                    if subtitle == "" or ("[ SPACE" in subtitle) or subtitle.startswith("[B]"):
                        pass
                    else:
                        srt_in = sec_to_srttime(offset / FCPX_SCALE)
                        srt_out = sec_to_srttime((duration + offset) / FCPX_SCALE)
                        if srt_in == srt_out:
                            eprint("WARNING: zero length srt. angry FCPX", offset, duration, fcpx_record_in, fcpx_record_out, srt_in, srt_out)
                        srt_queue.append("%d"%srt_counter)
                        srt_queue.append("%s --> %s"%(srt_in, srt_out))
                        srt_queue.append("%s"%subtitle.replace("\\N", "\n"))
                        srt_queue.append("")
                        srt_counter += 1
            else:
                continue

            if subtitle.startswith("[B]"): #B-roll, EDL 00:00:00,000    00:00:01,000    | somevideo |   [B] b-roll
                output_queue_B.append([ clipname, ref_id, offset, fcpx_record_in, duration, 1, subtitle ]) #1 stands for lane='1'
            else: #Normal lines
                output_queue.append([ clipname, ref_id, offset, fcpx_record_in, duration, 0, subtitle ]) #0 can be ignored
                offset += duration

    ####### Stitching #######
    if len(output_queue) > 99999 or len(output_queue_B) > 99999:
        eprint("Too much. That's too much.")
        sys.exit(-1)
    # stitch adjecent clips in output_queue
    before_stitch_lines = len(output_queue)
    output_queue = stitch_fcpxml_queue(output_queue)
    after_stitch_lines = len(output_queue)
    eprint("[stitch] %d --> %d lines"%(before_stitch_lines, after_stitch_lines))
    # stitch adjecent clips in output_queue_B
    before_stitch_lines_B = len(output_queue_B)
    if before_stitch_lines_B > 0:
        output_queue_B = stitch_fcpxml_queue(output_queue_B)
        after_stitch_lines_B = len(output_queue_B)
        eprint("[stitch B] %d --> %d lines"%(before_stitch_lines_B, after_stitch_lines_B))

    for k in media_assets:
        xmlhead += xmlheader2.format(ref_id=media_assets[k][1] , mediapath = urllib.parse.quote(media_assets[k][0]), hasVideo=media_assets[k][2], hasAudio=media_assets[k][3], duration = media_assets[k][4])
        if is_pure_audio:
            eprint("WARNING & FIXME: hasVideo=0, if you want to import into DaVinci Resolve as a multicam. You may change it in .fcpxml manually")
    xmlhead += xmlheader3
    print(xmlhead)

    for _clipname, _ref_id, _offset, _fcpx_record_in, _duration, _lane, _subtitle in output_queue:
        index_B = find_b_roll_of_clip(_offset, _duration, output_queue_B)
        if  len(index_B) != 0:  # B roll found
            if media_assets[_clipname][5] == 1: # A clip is Still Picture
                xmlbody += '<video ref="{ref_id}" offset="{offset}/{fcpx_scale}s" name="{clipname}" start="{start}/{fcpx_scale}s" duration="{duration}/{fcpx_scale}s">\n'.format(
                        clipname = _clipname, ref_id = _ref_id, offset =  _offset,
                        start = _fcpx_record_in, duration = _duration, fcpx_scale = FCPX_SCALE)  # A roll
                xmlbody += '    <note>' + _subtitle + '</note>\n'
                _tail = '</video>\n'
            else: # Video or Audio
                xmlbody += '<asset-clip ref="{ref_id}" offset="{offset}/{fcpx_scale}s" name="{clipname}" start="{start}/{fcpx_scale}s" duration="{duration}/{fcpx_scale}s" audioRole="dialogue">\n'.format(
                        clipname = _clipname, ref_id = _ref_id, offset =  _offset,
                        start = _fcpx_record_in, duration = _duration, fcpx_scale = FCPX_SCALE)  # A roll
                xmlbody += '    <note>' + _subtitle + '</note>\n'
                _tail = '</asset-clip>\n'

            for i in index_B:
                _clipname_B, _ref_id_B, _offset_B, _fcpx_record_in_B, _duration_B, _lane_B, _subtitle_B = output_queue_B[i] #get B roll clip information
                if media_assets[_clipname_B][5] == 1: # B roll clip is still picture
                    xmlbody += '    <video ref="{ref_id}" lane="{lane}" offset="{offset}/{fcpx_scale}s" name="{clipname}"  start="{start}/{fcpx_scale}s" duration="{duration}/{fcpx_scale}s">\n'.format(
                            clipname = _clipname_B, ref_id = _ref_id_B, offset = _offset_B + _fcpx_record_in - _offset,
                            start = _fcpx_record_in_B, duration = _duration_B, fcpx_scale = FCPX_SCALE, lane = _lane_B)  # B roll clip
                    xmlbody += '    <note>' + _subtitle_B + '</note>\n'
                    xmlbody += '    </video>\n'
                else:
                    xmlbody += '    <asset-clip ref="{ref_id}" lane="{lane}" offset="{offset}/{fcpx_scale}s" name="{clipname}"  start="{start}/{fcpx_scale}s" duration="{duration}/{fcpx_scale}s">\n'.format(
                            clipname = _clipname_B, ref_id = _ref_id_B, offset = _offset_B + _fcpx_record_in - _offset,
                            start = _fcpx_record_in_B, duration = _duration_B, fcpx_scale = FCPX_SCALE, lane = _lane_B)  # B roll clip
                    xmlbody += '    <note>' + _subtitle_B + '</note>\n'
                    xmlbody += '    </asset-clip>\n'
            #FIXME
            #for i in index_B:
            #    del(output_queue_B[i])
            xmlbody += _tail
        else:  # No B roll
            if media_assets[_clipname][5] == 1: # A clip is Still Picture
                xmlbody += '<video name="{clipname}" ref="{ref_id}" offset="{offset}/{fcpx_scale}s" start="{start}/{fcpx_scale}s" duration="{duration}/{fcpx_scale}s" lane="{lane}">\n'.format(
                        clipname = _clipname, ref_id = _ref_id, offset =  _offset, start = _fcpx_record_in, duration = _duration, fcpx_scale = FCPX_SCALE, lane = _lane)
                xmlbody += '<note>' + _subtitle + '</note>\n'
                xmlbody += '</video>\n'
            else: # A clip
                xmlbody += '<asset-clip name="{clipname}" ref="{ref_id}" offset="{offset}/{fcpx_scale}s" start="{start}/{fcpx_scale}s" duration="{duration}/{fcpx_scale}s" audioRole="dialogue" lane="{lane}">\n'.format(
                        clipname = _clipname, ref_id = _ref_id, offset =  _offset, start = _fcpx_record_in, duration = _duration, fcpx_scale = FCPX_SCALE, lane = _lane)
                xmlbody += '<note>' + _subtitle + '</note>\n'
                xmlbody += '</asset-clip>\n'
                #xmlbody += "%s\t%s\t%s\t%s\t%s\n"%(clipname, ref_id, offset, fcpx_record_in, duration) #DEBUG

    print(xmlbody)
    print(xmltail)

    srt_filename = "fcpxml.srt"
    if GENERATE_SRT:
        eprint("[srt] writing ",srt_filename)
        with open(srt_filename, "w") as output_file:
            output_file.write('\n'.join(srt_queue))
