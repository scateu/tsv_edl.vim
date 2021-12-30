#!/usr/bin/env python3
import sys

"""
EDL	00:03:34,875	00:03:38,208	| VfD E04 The Terahertzian |	tell us what 1 terahertz is in
"""

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

if __name__ == "__main__":
    counter = 0
    last_position = 0.0 #in sec
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        if (line.startswith('EDL') or line.startswith('---') or line.startswith("xxx")) and not ('[ SPACE' in line):
            _l = line.strip()
            fields = _l.split('\t')
            if fields[1].count(":") == 2 and fields[2].count(":") == 2:
                if counter != 0: #not first block
                    print("")
                print(counter)
                t2 = srttime_to_sec(fields[2])
                t1 = srttime_to_sec(fields[1])
                duration = t2 - t1
                print("%s --> %s"%(sec_to_srttime(last_position), sec_to_srttime(last_position + duration)))
                print(fields[4])
                last_position += duration
            counter += 1
