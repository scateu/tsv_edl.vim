#!/usr/bin/env python3
import sys

"""
EDL	00:03:34,875	00:03:38,208	| VfD E04 The Terahertzian |	tell us what 1 terahertz is in
"""

if __name__ == "__main__":
    counter = 1
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        #if (line.startswith('EDL') or line.startswith('---') or line.startswith("xxx")) and not ('[ SPACE' in line):
        if (line.startswith('EDL') or line.startswith('---') ) and not ('[ SPACE' in line):
            _l = line.strip()
            fields = _l.split('\t')
            if fields[1].count(":") == 2 and fields[2].count(":") == 2:
                if counter != 0: #not first block
                    print("")
                print(counter)
                print("%s --> %s"%(fields[1], fields[2]))
                if len(fields) == 4:
                    fields.append("")  #empty subtitle, make fields[4] exist
                print(fields[4].replace("\\N",'\n'))
                counter += 1
