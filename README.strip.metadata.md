# Strip Metadata

Sometime you got a .mov file that looks like

```
$ mediainfo some.mov

[...]
Time code of first frame                 : 01:00:00:00
Time code of last frame                  : 01:00:08:21
Time code, stripped                      : Yes
[...]
```

When exported to .fcpxml, those clips will not be matched because `tsv2fcpxml` will write timecode from `00:00:00,000`.

1. You may use ` cat some.tsv | tsv2fcpxml --fps=25 --nosrt --offsetonehour  > some.fcpxml`
2. You may strip it with

    ffmpeg -i in.mov -map_metadata -1 -c:v copy -c:a copy out.mov
