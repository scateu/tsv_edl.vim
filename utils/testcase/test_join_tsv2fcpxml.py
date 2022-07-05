def stitch_fcpxml_queue(raw_queue):
    #([clipname, ref_id, offset, fcpx_record_in, duration ])
    length = len(raw_queue)
    stitched_output = [] 
    i = 0
    while i < length:
        clip, ref_id, offset, t1, duration = raw_queue[i]
        t2 = t1 + duration
        j = i + 1
        if (i == length - 1): #last line
            stitched_output.append(raw_queue[i])
            break
        clip_next, ref_id_next, offset_next, t1_next, duration_next = raw_queue[j]
        t2_next = t1_next + duration_next
        _item = [clip, ref_id, offset, t1, duration]
        while (clip == clip_next and t2 == t1_next):
            t2_next = t1_next + duration_next
            _item = [clip, ref_id, offset, t1, t2_next] #update pending output
            clip, ref_id, offset, t1, t2 = _item #update item on the left to be examined
            j += 1
            if (j == length): #out of index
                break
            clip_next, ref_id_next, offset_next, t1_next, duration_next = raw_queue[j]
            t2_next = duration_next - t1_next
        stitched_output.append(_item)
        i = j
    return stitched_output

def testit(a,b):
    result = stitch_edl_queue(a)
    if result == b:
        print("pass")
    else:
        print("fail")
        print(result)

#raw_queue = [['a','b','c'],['d','e','f']]
#answer = [['a','b','c'],['d','e','f']]
#testit(raw_queue,answer)
#
#raw_queue = [['a.mp4',"00:00:01.123", "00:01:03.345"], ['a.mp4', "00:01:03.345", "00:09:03.345"], ]
#answer = [['a.mp4', '00:00:01.123', '00:09:03.345']]
#testit(raw_queue,answer)
#
#
#raw_queue = [
#        ['a.mp4',"00:00:01.123", "00:01:03.345"], 
#        ['a.mp4', "00:01:03.345", "00:02:03.345"],
#        ['b.mp4', "00:02:03.345", "00:02:05.345"],
#        ['b.mp4', "00:02:05.345", "00:04:03.345"],
#        ['b.mp4', "00:08:05.345", "00:09:03.345"],
#        ]
#answer = [['a.mp4', '00:00:01.123', '00:02:03.345'], ['b.mp4', '00:02:03.345', '00:04:03.345'], ['b.mp4', '00:08:05.345', '00:09:03.345']]
#testit(raw_queue,answer)
#
#
#raw_queue = [['a.mp4',"00:00:01.123", "00:01:03.345"],]
#answer = [['a.mp4', '00:00:01.123', '00:01:03.345']]
#testit(raw_queue,answer)
#
#raw_queue = [['a.mp4',"00:00:01.123", "00:01:03.345"], ['b.mp4', "00:08:05.345", "00:09:03.345"]]
#answer  = [['a.mp4', '00:00:01.123', '00:01:03.345'], ['b.mp4', '00:08:05.345', '00:09:03.345']]
#testit(raw_queue,answer)
#
#
#raw_queue = [['InglouriousBastards.mkv', '00:00:36,660', '00:00:40,123'], ['InglouriousBastards.mkv', '00:00:40,123', '00:00:40,874'], ['InglouriousBastards.mkv', '00:00:40,874', '00:00:45,838'], ['InglouriousBastards.mkv', '00:00:45,838', '00:00:46,760'], ['InglouriousBastards.mkv', '00:00:46,760', '00:00:49,591'], ['InglouriousBastards.mkv', '00:00:49,591', '00:00:50,470'], ['InglouriousBastards.mkv', '00:00:50,470', '00:00:52,427'], ['InglouriousBastards.mkv', '00:00:52,427', '00:00:53,550'], ['InglouriousBastards.mkv', '00:00:53,550', '00:00:56,014'], ['InglouriousBastards.mkv', '00:00:56,014', '00:00:57,350'], ['InglouriousBastards.mkv', '00:00:57,350', '00:00:59,852'], ['InglouriousBastards.mkv', '00:00:59,852', '00:01:01,140'], ['InglouriousBastards.mkv', '00:01:01,140', '00:01:03,564'], ['InglouriousBastards.mkv', '00:01:03,564', '00:01:05,230'], ['InglouriousBastards.mkv', '00:01:05,230', '00:01:07,609'], ['InglouriousBastards.mkv', '00:01:07,609', '00:01:08,780'], ['InglouriousBastards.mkv', '00:01:08,780', '00:01:11,321'], ['InglouriousBastards.mkv', '00:01:11,321', '00:01:12,280'], ['InglouriousBastards.mkv', '00:01:12,280', '00:01:15,617'], ['InglouriousBastards.mkv', '00:01:15,617', '00:01:52,245']]
#answer = [['InglouriousBastards.mkv', '00:00:36,660', '00:01:52,245']]
#testit(raw_queue,answer)
#
#raw_queue = [['','',''],['','',''],['','','']]
#answer = [['','','']]
#testit(raw_queue,answer)
#
#raw_queue = [['a','b','c'],['d','e','f'], ['','',''], ['','','']]
#answer = [['a','b','c'],['d','e','f'], ['','','']]
#testit(raw_queue,answer)
#
