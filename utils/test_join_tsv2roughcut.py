def stitch_edl_queue(raw_queue):
    stitched_output = [] 
    i = 0
    while i < len(raw_queue):
        clip, t1, t2 = raw_queue[i]
        j = i + 1
        if j == len(raw_queue):
            break
        #print(i,j)
        clip_next, t1_next, t2_next = raw_queue[j]
        _item = [clip, t1, t2]
        while (clip == clip_next and t2 == t1_next):
            _item = [clip, t1, t2_next]
            clip, t1, t2 = _item
            j += 1
            if j < len(raw_queue) - 1:
                clip_next, t1_next, t2_next = raw_queue[j]
            else: # j is out of index
                break
        stitched_output.append(_item)
        i = j
        #print(i,j)
    return stitched_output

raw_queue = [['a.mp4',"00:00:01.123", "00:01:03.345"], ['a.mp4', "00:00:03.345", "00:09:03.345"], ]
print(stitch_edl_queue(raw_queue))
#import sys;sys.exit()

raw_queue = [['a.mp4',"00:00:01.123", "00:01:03.345"], 
        ['a.mp4', "00:01:03.345", "00:02:03.345"],
        ['b.mp4', "00:02:03.345", "00:02:05.345"],
        ['b.mp4', "00:02:05.345", "00:04:03.345"],
        ['b.mp4', "00:08:05.345", "00:09:03.345"],
        ]
print(stitch_edl_queue(raw_queue))

raw_queue = [['a.mp4',"00:00:01.123", "00:01:03.345"],]
print(stitch_edl_queue(raw_queue))

raw_queue = [['a.mp4',"00:00:01.123", "00:01:03.345"],
        ['b.mp4', "00:08:05.345", "00:09:03.345"],
        ]
print(stitch_edl_queue(raw_queue))

raw_queue = [['InglouriousBastards.mkv', '00:00:36,660', '00:00:40,123'], ['InglouriousBastards.mkv', '00:00:40,123', '00:00:40,874'], ['InglouriousBastards.mkv', '00:00:40,874', '00:00:45,838'], ['InglouriousBastards.mkv', '00:00:45,838', '00:00:46,760'], ['InglouriousBastards.mkv', '00:00:46,760', '00:00:49,591'], ['InglouriousBastards.mkv', '00:00:49,591', '00:00:50,470'], ['InglouriousBastards.mkv', '00:00:50,470', '00:00:52,427'], ['InglouriousBastards.mkv', '00:00:52,427', '00:00:53,550'], ['InglouriousBastards.mkv', '00:00:53,550', '00:00:56,014'], ['InglouriousBastards.mkv', '00:00:56,014', '00:00:57,350'], ['InglouriousBastards.mkv', '00:00:57,350', '00:00:59,852'], ['InglouriousBastards.mkv', '00:00:59,852', '00:01:01,140'], ['InglouriousBastards.mkv', '00:01:01,140', '00:01:03,564'], ['InglouriousBastards.mkv', '00:01:03,564', '00:01:05,230'], ['InglouriousBastards.mkv', '00:01:05,230', '00:01:07,609'], ['InglouriousBastards.mkv', '00:01:07,609', '00:01:08,780'], ['InglouriousBastards.mkv', '00:01:08,780', '00:01:11,321'], ['InglouriousBastards.mkv', '00:01:11,321', '00:01:12,280'], ['InglouriousBastards.mkv', '00:01:12,280', '00:01:15,617'], ['InglouriousBastards.mkv', '00:01:15,617', '00:01:52,245']]
print(stitch_edl_queue(raw_queue))
