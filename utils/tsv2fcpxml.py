#!/usr/bin/env python3
#-*- coding:utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import urllib.parse
import os
import glob
import sys

video_formats = ['mkv', 'mp4', 'mov', 'mpeg', 'ts', 'avi']

xmlheader1 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>

<fcpxml version="1.8">
    <resources>
        <format id="r1" frameDuration="3750/90000s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>
"""
xmlheader2 = """
        <asset id="{ref_id}" src="file://{mediapath}" start="0s" duration="6240s" hasVideo="1" hasAudio="1" format="r1" audioSources="1" audioChannels="1" audioRate="48000" />
"""
xmlheader3 = """
    </resources>
    <library>
        <event name="DEFAULT">
            <project name="DEFAULT">
                <sequence duration="15720000/90000s" format="r1" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
                    <spine>
"""

#TODO: 用模板语言?

xmltail = """                    </spine>
                </sequence>
            </project>
        </event>
    </library>
</fcpxml>
"""

"""
         |     s     |  gap    | s_next    |
       start        end         

<asset-clip name="MyMovie3" ref="r2" offset="5s" start="15s" duration="5s" audioRole="dialogue" /> 
"""

def timecode_to_fcpx_time(timecode, fcp_scale=90000, FPS=24):
    timecode = timecode.strip().replace(",", ":")
    h,m,s,ms = [int(d) for d in timecode.split(":")]
    # round to frames
    ms_scaled = int(ms/1000.0 * FPS) * (fcp_scale / FPS)  #frames * 3750/90000 * 90000
    return h*3600*fcp_scale + m*60*fcp_scale + s*fcp_scale + ms_scaled


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    media_assets = {} # { "clipname": [ abspath, ref_id ] , ... }
    xmlhead = ""
    xmlbody = ""
    xmlhead += xmlheader1
    offset = 0
    eprint("NOTE: 24FPS, 48000Hz. Bite me.")
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        if line.startswith('EDL'):
            _l = line.strip()
            if _l.count('|'):
                clipname = _l.split('|')[1].strip()
                filenames_v = [ c for c in glob.glob("*%s*"%clipname) if os.path.splitext(c)[1][1:].lower() in video_formats ]
                if len(filenames_v) > 0:
                    abspath = os.path.abspath(filenames_v[0])
                else:
                    abspath = clipname
                if not clipname in media_assets:
                    ref_id = "r%d"%(len(media_assets) + 2) #id start from r2
                    media_assets[clipname] = [abspath, ref_id ] 
                else:
                    ref_id = media_assets[clipname][1]
                _l = _l.split('|')[0]
            else:
                continue
            _l = _l.split() #['EDL', '01:26:16.12', '01:27:22.10']
            record_in = timecode_to_fcpx_time(_l[1])
            record_out  = timecode_to_fcpx_time(_l[2])
            duration = record_out - record_in
            xmlbody += "<asset-clip name=\"%s\" ref=\"%s\" offset=\"%d/90000s\" start=\"%d/90000s\" duration=\"%d/90000s\" audioRole=\"dialogue\" />\n"%(clipname, ref_id, offset, record_in, duration)
            #xmlbody += "%s\t%s\t%s\t%s\t%s\n"%(clipname, ref_id, offset, record_in, duration) #DEBUG
            offset += duration 
    for k in media_assets:
        xmlhead += xmlheader2.format(ref_id=media_assets[k][1] , mediapath = urllib.parse.quote(media_assets[k][0]))
    xmlhead += xmlheader3
    print(xmlhead)
    print(xmlbody)
    print(xmltail)
