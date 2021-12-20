#!/usr/bin/env python3
import sys
import glob

"""
EDL	00:03:34,875	00:03:38,208	| VfD E04 The Terahertzian |	tell us what 1 terahertz is in
"""

for file_name in glob.glob('*.tsv'):
    with open(file_name, encoding='utf8') as file_in:
        try:
            str_in = file_in.read()
        except:
            with open(file_name, encoding='gbk') as f:
                str_in = f.read()
        counter = 0
        lines = str_in.split('\n')
        str_out = []

        with open(file_name.replace('.tsv', '.srt'), 'w', encoding='utf8') as file_out:
            print("open %s to write ..."%file_out.name)
            for line in lines:
                if not line:
                    continue
                if line.startswith('EDL') or line.startswith('---') or line.startswith("xxx"):
                    _l = line.strip()
                    fields = _l.split('\t')
                    if fields[1].count(":") == 2 and fields[2].count(":") == 2:
                        if counter != 0:
                            file_out.write('\n')
                        file_out.write("%d"%counter)
                        file_out.write('\n')
                        file_out.write("%s --> %s"%(fields[1], fields[2]))
                        file_out.write('\n')
                        file_out.write(fields[4])
                        file_out.write('\n')
                    counter += 1
