# Tutorial: Export to DaVinci and Multicam Edit

## INPUT

 1. Camera A
 2. Camera B
 3. Audio Recording: audiofile.m4a

## 1. Audio Recording

 - Find the slate position (👏/🎬). Trim off all audio before. 
 - Export, so that the audio starts with a slate sound. 
 - Transcribe it.
 - do `srt2tsv_all`
 - paper edit
 - do `cat roughcut.tsv | sed 's/audiofile/multicam/' | tsv2fcpxml > multicam.fcpxml `
   - or: ` cat roughcut.tsv | tsv2fcpxml --fps=25 --nosrt --offsetonehour  > multicam.fcpxml`
	   - **FPS**: Make sure your audio/video/tsv2fcpxml use the same FPS setting

## 2. Import to DaVinci Resolve
 - Import audiofile.m4a
 - Import footage A from SD Card into DaVinci Resolve
 - Import footage B from SD Card 

 - ~~Search for slate position in footage A.~~
   - ~~Press `I` to set as "In Mark".~~
 - ~~Do the same to footage B~~

 - Click on audiofile, footage A and footage B. Right click - "New Multicam Clip"
   - Start Timecode: 01:00:00:00  (thanks to `--offsetonehour`)
   - Frame Rate: 25 (as specified in `tsv2fcpxml.py`)
   - Angle Sync: Sound (Or with In Mark)
   - Name: `multicam`

 - Import `multicam.fcpxml`
   - **Uncheck** "Automatically import source clips into media pool"
   - **Check only** the bin that includes `multicam` clip. So that it's easier for DaVinci Resolve to select this one
 - Tada! DaVinci Resolve should be using your Multicam Clip named `multicam`

## 3. Edit!

 - ~~Cmd-A on timeline~~
 - ~~Right click, Link~~
 - ~~Right click, Unlink~~
 - ~~Select all Audio clips. Menu - Multicam Switch to Angel 1 (The good audio)~~
 - ~~Lock Audio Track.~~
 - ~~Select all Video clips. Menu - Multicam Switch to Angel 2/3 (Select one default video)~~

 - '🔽' key to select next clip
 - 'Option-2' to switch angel

### Edit along with Subtitles
 - Import SRT
 - Check off "Selection Follows Playhead"
 - Mark In
 - Mark Out
     - Make sure no clip is selected and In/Out region is highlighted
 - Ripple Delete
 - Boom! Audio, Multicam and Subtitle will be removed all at once


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
