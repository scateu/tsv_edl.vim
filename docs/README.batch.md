# Batch add overley and credit

For example, for vertical influencers, 

1. Change all 1920 1080 accordingly in `tsv2roughcut.py`
2. something like this `do.sh`

```bash
#!/bin/bash

secs2timecode() {
	local line
	while read line; do
		h=$(bc <<< "$line/3600")
		m=$(bc <<< "($line%3600)/60")
		s=$(bc <<< "$line%60")
		printf "%02d:%02d:%06.3f\n" $h $m $s
		#| sed 's/\./,/' >> /tmp/b
	done
}

shopt -s nullglob

for i in *.mp4 *.MP4
    do 
	    echo $i
	    duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $i | secs2timecode | sed 's/\./,/g')
	    echo $duration
	    cat TEMPLATE.tsv | sed "s/TIMECODE/${duration}/g" | sed "s/FILENAME/${i%%.*}/"
	    cat TEMPLATE.tsv | sed "s/TIMECODE/${duration}/g" | sed "s/FILENAME/${i%%.*}/" | python3 tsv2roughcut.py
	    mv roughcut.mp4 rCut_${i%%.*}.mp4
	    rm roughcut.srt 
    done
```


TEMPLATE.tsv:

```
EDL	00:00:00,000	TIMECODE	| overlay |	[B] Overlay
EDL	00:00:00,000	TIMECODE	| FILENAME |	Main Video
EDL	00:00:00,000	00:00:02,000	| something1 |	Credit 1
EDL	00:00:00,000	00:00:02,000	| something2 |	Credit 2
```



## See also: AI generated do.py from do.sh

```python

#!/usr/bin/env python3
import subprocess
import glob
import os
from decimal import Decimal

def secs2timecode(seconds):
    """将秒数转换为时间码格式 HH:MM:SS.mmm"""
    seconds = Decimal(seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

def get_video_duration(filename):
    """使用 ffprobe 获取视频时长"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        filename
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def process_video(video_file):
    """处理单个视频文件"""
    print(video_file)

    # 获取视频时长并转换为时间码
    duration = get_video_duration(video_file)
    timecode = secs2timecode(duration)
    timecode = timecode.replace('.', ',')
    print(timecode)

    # 获取不带扩展名的文件名
    filename_without_ext = os.path.splitext(video_file)[0]

    # 读取并处理模板文件
    with open('模板.tsv', 'r', encoding='utf-8') as f:
        template_content = f.read()

    # 替换模板中的占位符
    processed_content = template_content.replace('TIMECODE', timecode).replace('FILENAME', filename_without_ext)

    # 将处理后的内容传递给 tsv2roughcut.py
    subprocess.run(['python3', 'tsv2roughcut.py'], input=processed_content.encode(), check=True)

    # 重命名输出文件
    output_filename = f"糙_{filename_without_ext}.mp4"
    os.rename('roughcut.mp4', output_filename)

    # 删除临时字幕文件
    if os.path.exists('roughcut.srt'):
        os.remove('roughcut.srt')

def main():
    """主函数"""
    # 获取所有 MP4 文件（不区分大小写）
    video_files = glob.glob('*.mp4') + glob.glob('*.MP4')

    # 处理每个视频文件
    for video_file in video_files:
        try:
            process_video(video_file)
        except Exception as e:
            print(f"处理 {video_file} 时出错: {e}")

if __name__ == '__main__':
    main()

```
