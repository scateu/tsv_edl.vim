# B Roll

Add `[B]` right in the beginning of the subtitle section, i.e., right after the 'TAB' character. Then this line will be treated as a B-roll, `lane=1` set in fcpxml.

```
EDL 00:00:00,000    00:00:01,000    | some video |  [B] this line will be treated as B-roll
EDL 00:03:02,000    00:03:04,000    | A roll video |  normal lines
EDL 00:03:04,000    00:03:09,000    | A roll video |  more normal lines
```

It works in `tsv2fcpxml` now.

 - [ ] Support in tsv2roughcut
 - [X] Only supported in Davinci Resolve. FCPX doesn't work.
 - [ ] FPS conform


# FCPXML samples

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.8">
    <resources>
        <format name="FFVideoFormat1080p24" height="1080" width="1920" id="r0" frameDuration="1/24s"/>
        <format name="FFVideoFormat720p25" height="720" width="1280" id="r1" frameDuration="1/25s"/>
        <format name="FFVideoFormat1080p30" height="1080" width="1920" id="r3" frameDuration="1/30s"/>
        <format name="FFVideoFormatRateUndefined" height="2064" width="3522" id="r5"/>
        <asset audioSources="1" name="Jack Ma- Love is Important In Business | Davos 2018.mp4" hasVideo="1" audioChannels="2" hasAudio="1" start="0/1s" src="file:///Users/K/CUT/Jack%20Ma-%20Love%20is%20Important%20In%20Business%20%7C%20Davos%202018.mp4" duration="83479/25s" id="r2" format="r1"/>
        <asset audioSources="1" name="2023-01-24-咖啡压粉萝卜章.mov" hasVideo="1" audioChannels="2" hasAudio="1" start="0/1s" src="file:///Users/K/CUT/2023-01-24-%E5%92%96%E5%95%A1%E5%8E%8B%E7%B2%89%E8%90%9D%E5%8D%9C%E7%AB%A0.mov" duration="131/15s" id="r4" format="r3"/>
        <asset name="Screenshot 2023-03-12 at 21.23.55.png" hasVideo="1" start="0/1s" src="file:///Users/K/Desktop/Screenshot%202023-03-12%20at%2021.23.55.png" duration="0/1s" id="r6" format="r5"/>
    </resources>
    <library>
        <event name="d (Resolve)">
            <project name="d (Resolve)">
                <sequence tcFormat="NDF" duration="551/24s" format="r0" tcStart="0/1s">
                    <spine>
                        <asset-clip name="Jack Ma- Love is Important In Business | Davos 2018.mp4" enabled="1" tcFormat="NDF" start="1206/25s" ref="r2" duration="49/12s" offset="0/1s" format="r1">
                            <conform-rate srcFrameRate="25"/>
                            <adjust-conform type="fit"/>
                            <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                        </asset-clip>
                        <asset-clip name="Jack Ma- Love is Important In Business | Davos 2018.mp4" enabled="1" tcFormat="NDF" start="1304/25s" ref="r2" duration="5/3s" offset="49/12s" format="r1">
                            <conform-rate srcFrameRate="25"/>
                            <adjust-conform type="fit"/>
                            <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            <asset-clip lane="1" name="2023-01-24-咖啡压粉萝卜章.mov" enabled="1" tcFormat="NDF" start="13/12s" ref="r4" duration="3/4s" offset="1304/25s" format="r3">
                                <adjust-conform type="fit"/>
                                <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            </asset-clip>
                        </asset-clip>
                        <asset-clip name="Jack Ma- Love is Important In Business | Davos 2018.mp4" enabled="1" tcFormat="NDF" start="407/5s" ref="r2" duration="19/8s" offset="23/4s" format="r1">
                            <conform-rate srcFrameRate="25"/>
                            <adjust-conform type="fit"/>
                            <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            <video lane="1" name="图片" enabled="1" start="0/1s" ref="r6" duration="49/24s" offset="407/5s">
                                <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            </video>
                        </asset-clip>
                        <asset-clip name="Jack Ma- Love is Important In Business | Davos 2018.mp4" enabled="1" tcFormat="NDF" start="2246/25s" ref="r2" duration="17/3s" offset="65/8s" format="r1">
                            <conform-rate srcFrameRate="25"/>
                            <adjust-conform type="fit"/>
                            <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                        </asset-clip>
                        <asset-clip name="Jack Ma- Love is Important In Business | Davos 2018.mp4" enabled="1" tcFormat="NDF" start="15382/25s" ref="r2" duration="3/1s" offset="331/24s" format="r1">
                            <conform-rate srcFrameRate="25"/>
                            <adjust-conform type="fit"/>
                            <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            <asset-clip lane="1" name="2023-01-24-咖啡压粉萝卜章.mov" enabled="1" tcFormat="NDF" start="13/12s" ref="r4" duration="3/4s" offset="15382/25s" format="r3">
                                <adjust-conform type="fit"/>
                                <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            </asset-clip>
                        </asset-clip>
                        <asset-clip name="Jack Ma- Love is Important In Business | Davos 2018.mp4" enabled="1" tcFormat="NDF" start="67776/25s" ref="r2" duration="23/12s" offset="403/24s" format="r1">
                            <conform-rate srcFrameRate="25"/>
                            <adjust-conform type="fit"/>
                            <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                        </asset-clip>
                        <asset-clip name="Jack Ma- Love is Important In Business | Davos 2018.mp4" enabled="1" tcFormat="NDF" start="15386/5s" ref="r2" duration="17/4s" offset="449/24s" format="r1">
                            <conform-rate srcFrameRate="25"/>
                            <adjust-conform type="fit"/>
                            <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            <asset-clip lane="1" name="2023-01-24-咖啡压粉萝卜章.mov" enabled="1" tcFormat="NDF" start="13/12s" ref="r4" duration="3/4s" offset="15386/5s" format="r3">
                                <adjust-conform type="fit"/>
                                <adjust-transform position="0 0" anchor="0 0" scale="1 1"/>
                            </asset-clip>
                        </asset-clip>
                    </spine>
                </sequence>
            </project>
        </event>
    </library>
</fcpxml>
```
