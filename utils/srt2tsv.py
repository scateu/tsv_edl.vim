#!/usr/bin/env python3
'''
modified from https://raw.githubusercontent.com/bojiang/srt2lrc/master/srt2lrc.py
Run it in srt file folder.
python 3.x
'''
import glob
import re
import argparse
import sys

CLOSE_GAPS = True

SRT_BLOCK_REGEX = re.compile(
        r'(\d+)[^\S\r\n]*[\r\n]+'
        r'(\d{2}:\d{2}:\d{2},\d{3,4})[^\S\r\n]*-->[^\S\r\n]*(\d{2}:\d{2}:\d{2},\d{3,4})[^\S\r\n]*[\r\n]+'
        r'([\s\S]*)')

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

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
    with open(fname, encoding='utf8') if fname != "-" else sys.stdin as file_in:
        if fname == '-': #stdin. _CLIPNAME_ for placeholder in output
            fname ="_CLIPNAME_"

        try:
            str_in = file_in.read()
        except:
            with open(fname, encoding='gbk') if fname != "-" else sys.stdin as f:
                str_in = f.read()
        blocks_in = str_in.replace('\r\n', '\n').split('\n\n')
        blocks_out = [srt_block_to_tsv(block, fname) for block in blocks_in]
        if not all(blocks_out):
            err_info.append((fname, blocks_out.index(None), blocks_in[blocks_out.index(None)]))
        blocks_out = filter(None, blocks_out)
        str_out = ''.join(blocks_out)

        if CLOSE_GAPS:
            eprint("CLOSE_GAPS: will use the next In TC as current Out TC.")
            eprint("CLOSE_GAPS: threshold 0.3sec")
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

        #utf-8-sig will add UTF-8 BOM HEADER EF BB BF. courtesy of BG5HHP
        with open(fname.replace('.srt', '.tsv'), 'w', encoding='utf-8-sig') if fname != "_CLIPNAME_" else sys.stdout as file_out:
            file_out.write("EDL\tRecord In\tRecord Out\tClipname\tSubtitle\n")
            file_out.write(str_out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("srtfile", nargs='*', help="file name for input. multiple supported. if none provided, use stdin")
    parser.add_argument("-a", "--all", action="store_true", help="handle all srt file in current directory")
    args = parser.parse_args()

    err_info = []
    if args.all: # handle all file 
        file_name = glob.glob('*.srt')
    elif args.srtfile:  #has file do 
        file_name = args.srtfile
    else: #stdin
        file_name = ['-']

    for f in file_name:
        try:
            srt_file_to_tsv(f)
            eprint("%s converted."%f)
        except Exception as e:
            eprint("%s failed, skip. reason: %s"%(f,e))
        if err_info:
            eprint('success, but some exceptions are ignored:')
            for file_name, blocks_num, context in err_info:
                eprint('\tfile: %s, block num: %s, context: %s' % (file_name, blocks_num, context))
        else:
            eprint('success')
