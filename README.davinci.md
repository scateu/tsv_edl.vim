# Tutorial Export to davinci. Multicam

INPUT:
 1. Camera A
 2. Camera B
 3. Audio Recording: audiofile.m4a

## 1. Audio Recording

 - Find the slate position (👏/🎬). Trim off all audio before. 
 - Export, so that the audio starts with a slate sound. 
 - Transcribe it.
 - do `srt2tsv_all`
 - edit, paper edit.
 - do `cat roughcut.tsv | sed 's/audiofile/multicam' | tsv2fcpxml > multicam.fcpxml `
   - **FPS**: Make sure your audio/video/tsv2fcpxml use the same FPS setting

## 2. Import to DaVinci Resolve
 - Import audiofile.m4a
 - Import footage A from SD Card into DaVinci Resolve
 - Import footage B from SD Card 

 - Search for slate position in footage A. 
   - Press `I` to set as "In Mark". 
 - Do the same to footage B
 - Click on audiofile, footage A and footage B. Right click - "New Multicam Clip"
   - Start Timecode: 00:00:00:00
   - Frame Rate: 24 (as specified in `tsv2fcpxml.py`)
   - Angle Sync: In
   - Name: multicam

 - Import multicam.fcpxml
   - **Uncheck** "Automatically import source clips into media pool"
   - **Check only** the bin that includes "multicam" clip. So that it's easier for DaVinci Resolve to select this one
 - Tada! DaVinci Resolve should be using your Multicam Clip named "multicam"

## 3. Edit!
 - On multicam pane, check 'audio only' button
 - Cmd-A on timeline
 - Option click on the good audio track. (Multicam Switch audio only)
 - Lock Audio 1 Track. 


# REFERENCES

```bash
ffmpeg -i CamB.mov -i audiofile.m4a -c:v copy -map 0:v:0 -map 1:a:0 CamB.mp4 
# replace the bad audio in footage with good audio

ffmpeg -i CamB.mov -ss 00:03:34.416 -c copy CamB_.mov

ffmpeg -i 220701-T001.WAV -ac 1 -c copy B.wav
# export mono(Left) from a stereo file

ffmpeg -i 220701-T001.WAV -ac 2 -c copy B.wav
```

# Another style

1. On footage A: find the slate position, trim off. Replace the audio with the good one.
1. On footage B: same
1. `cat roughcut.tsv | sed 's/audiofile/CamA' | tsv2fcpxml > CamA.xml`
1. `cat roughcut.tsv | sed 's/audiofile/CamB' | tsv2fcpxml > CamB.xml`
1. import each
1. copy one whole timeline, and paste on top of another
1. Press `D` to disable the view angle you don't like.
