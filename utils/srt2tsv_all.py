#!/usr/bin/env python3
'''
modified from https://raw.githubusercontent.com/bojiang/srt2lrc/master/srt2lrc.py
Run it in srt file folder.
python 3.x
'''
import glob
import re

CLOSE_GAPS = True

SRT_BLOCK_REGEX = re.compile(
        r'(\d+)[^\S\r\n]*[\r\n]+'
        r'(\d{2}:\d{2}:\d{2},\d{3,4})[^\S\r\n]*-->[^\S\r\n]*(\d{2}:\d{2}:\d{2},\d{3,4})[^\S\r\n]*[\r\n]+'
        r'([\s\S]*)')

def srt_block_to_tsv(block, fname):
    match = SRT_BLOCK_REGEX.search(block)
    if not match:
        return None
    num, ts, te, content = match.groups()
    #co = content.replace('\n', ' ') #multiple lines of subtitle
    co = content.replace('\n', '\\N') #multiple lines of subtitle
    return 'EDL\t{record_in}\t{record_out}\t| {clipname} |\t{comments}\n'.format(clipname=fname.replace(".srt","") ,record_in=ts, record_out=te, comments=co)

def srt_tc_to_seconds(srt_tc): #00:03:04,020
    assert(srt_tc.count(':') == 2)
    assert(srt_tc.count(',') == 1)
    assert(srt_tc.count(';') == 0)
    digits = [int(d) for d in srt_tc.replace(',',':').split(':')]
    return digits[0] * 3600 + digits[1] * 60 + digits[2] + digits[3]/1000

def srt_file_to_tsv(fname):
    with open(fname, encoding='utf8') as file_in:
        try:
            str_in = file_in.read()
        except:
            with open(fname, encoding='gbk') as f:
                str_in = f.read()
        blocks_in = str_in.replace('\r\n', '\n').split('\n\n')
        blocks_out = [srt_block_to_tsv(block, fname) for block in blocks_in]
        if not all(blocks_out):
            err_info.append((fname, blocks_out.index(None), blocks_in[blocks_out.index(None)]))
        blocks_out = filter(None, blocks_out)
        str_out = ''.join(blocks_out)

        if CLOSE_GAPS:
            print("CLOSE_GAPS: will use the next In TC as current Out TC.")
            print("CLOSE_GAPS: threshold 0.3sec")
            str_out_gaps_closed = ''
            lines = str_out.split('\n')[:-1] #the last line is empty
            for i in range(len(lines)-1): #don't touch the final line
                current_line = lines[i].split('\t')
                current_out_tc = current_line[2]
                next_in_tc = lines[i+1].split('\t')[1]

                gap_length = srt_tc_to_seconds(next_in_tc) - srt_tc_to_seconds(current_out_tc)
                if gap_length < 0.3:
                    current_line[2] =  next_in_tc #update current out with next_in_tc
                    str_out_gaps_closed += '\t'.join(current_line) + '\n'
                else: # add a "[SPACE]" clip
                    str_out_gaps_closed += '\t'.join(current_line) + '\n'
                    str_out_gaps_closed += '\t'.join(['EDL', current_out_tc, next_in_tc, current_line[3], "[ SPACE %.1f secs ]"%gap_length]) + '\n'
                #import pdb; pdb.set_trace()
            str_out_gaps_closed += lines[-1] #final line
            str_out_gaps_closed += '\n' #final line

            str_out = str_out_gaps_closed

        with open(fname.replace('.srt', '.tsv'), 'w', encoding='utf8') as file_out:
            file_out.write("EDL\tRecord In\tRecord Out\tClipname\tSubtitle\n")
            file_out.write(str_out)


if __name__ == '__main__':
    err_info = []
    for file_name in glob.glob('*.srt'):
        try:
            srt_file_to_tsv(file_name)
            print("%s converted."%file_name)
        except:
            print("%s failed, skip"%file_name)
    if err_info:
        print('success, but some exceptions are ignored:')
        for file_name, blocks_num, context in err_info:
            print('\tfile: %s, block num: %s, context: %s' % (file_name, blocks_num, context))
    else:
        print('success')

