# Tutorial: Export to DaVinci and Multicam Edit

## INPUT

 1. Camera A
 2. Camera B
 3. Audio Recording: audiofile.m4a

## 1. Audio Recording

 - Find the slate position (👏/🎬). Trim off all audio before. 
 - Export, so that the audio starts with a slate sound. 
 - Transcribe it.
 - do `srt2tsv -a`
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

### Edit along with Subtitles: I/O Style 
 - Import SRT
 - Check off "Selection Follows Playhead"
 - Mark In
 - Mark Out
     - Make sure no clip is selected and In/Out region is highlighted
 - Ripple Delete
 - Boom! Audio, Multicam and Subtitle will be removed all at once

### Edit along with Subtitles: Trim Items Start Style
 - Import SRT
 - If the SRT blocks on the right will be covering the left ones (blocks on the right has no gap), just do `Cmd-Shift-[`. (Trim > Ripple > Start to Playhead)
   - Otherwise, first delete all the SRT blocks you want to remove on the left


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

# sample of multicam.fcpxml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.8">
    <resources>
        <format id="r0" frameDuration="1001/30000s" name="FFVideoFormat1080p2997" width="1920" height="1080"/>
        <media id="r3" name="wwdc2022-10092 Multicam">
            <multicam tcStart="18018/5s" format="r0" tcFormat="NDF">
                <mc-angle name="Angle 2" angleID="2138e4ea-9aeb-4868-922a-11a9f9d072ec">
                    <asset-clip offset="0/1s" format="r0" ref="r1" enabled="1" start="0/1s" name="wwdc2022-10092.mp4" tcFormat="NDF" duration="60197137/30000s">
                        <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                    </asset-clip>
                </mc-angle>
                <mc-angle name="Angle 1" angleID="ed3a0aca-2865-4d64-9f26-6be657578be7">
                    <asset-clip offset="0/1s" format="r0" ref="r2" enabled="1" start="0/1s" name="wwdc2022-10092的副本.mp4" tcFormat="NDF" duration="60197137/30000s">
                        <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                    </asset-clip>
                </mc-angle>
            </multicam>
        </media>
        <asset id="r1" format="r0" src="file:///Users/k/CUT/infosec_cherrypick_tsvedl/WWDC_FIDO/wwdc2022-10092.mp4" hasVideo="1" start="0/1s" hasAudio="1" name="wwdc2022-10092.mp4" audioChannels="2" audioSources="1" duration="60197137/30000s"/>
        <asset id="r2" format="r0" src="file:///Users/k/CUT/infosec_cherrypick_tsvedl/WWDC_FIDO/wwdc2022-10092%E7%9A%84%E5%89%AF%E6%9C%AC.mp4" hasVideo="1" start="0/1s" hasAudio="1" name="wwdc2022-10092的副本.mp4" audioChannels="2" audioSources="1" duration="60197137/30000s"/>
    </resources>
    <library>
        <event name="Timeline 1 (Resolve)">
            <project name="Timeline 1 (Resolve)">
                <sequence tcStart="18018/5s" format="r0" tcFormat="NDF" duration="4637633/30000s">
                    <spine>
                        <mc-clip offset="18018/5s" ref="r3" start="126307181/30000s" name="wwdc2022-10092 Multicam" duration="122122/1875s">
                            <mc-source angleID="ed3a0aca-2865-4d64-9f26-6be657578be7" srcEnable="all">
                                <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            </mc-source>
                        </mc-clip>
                        <mc-clip offset="6878872/1875s" ref="r3" start="42753711/10000s" name="wwdc2022-10092 Multicam" duration="2683681/30000s">
                            <mc-source angleID="2138e4ea-9aeb-4868-922a-11a9f9d072ec" srcEnable="all">
                                <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            </mc-source>
                        </mc-clip>
                    </spine>
                </sequence>
            </project>
        </event>
    </library>
</fcpxml>
```
