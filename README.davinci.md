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

## 2. Import to DaVinci Resolve
 - Import audiofile.m4a
 - Import footage A from SD Card into DaVinci Resolve
 - Import footage B from SD Card 

 - Search for slate position in footage A. 
   - Press `I` to set as "In Mark". 
 - Do the same to footage B
 - Click on audiofile, footage A and footage B. Right click - "New Multicam Clip"
   - Start Timecode: 00:00:00:00
   - Angle Sync: In
   - Name: multicam

 - Import multicam.fcpxml. **Uncheck** "Automatically import source clips into media pool"
 - Tada! DaVinci Resolve should be using your Multicam Clip named "multicam"

## 3. Edit!
 - On multicam pane, check 'audio only' button
 - Cmd-A on timeline
 - Option click on the good audio track. (Multicam Switch audio only)


# REFERENCES

```bash
ffmpeg -i CamB.mov -i audiofile.m4a -c:v copy -map 0:v:0 -map 1:a:0 CamB.mp4 
# replace the bad audio in footage with good audio

ffmpeg -i CamB.mov -ss 00:03:34.416 -c copy CamB_.mov

ffmpeg -i 220701-T001.WAV -ac 1 -c copy B.wav
# export mono(Left) from a stereo file

ffmpeg -i 220701-T001.WAV -ac 2 -c copy B.wav
```
