# mpv waveform display as visual guide

A man (or woman) will be grateful if the following line is added to `~/.config/mpv/config`:

```
lavfi-complex='[aid1]asplit[ao][a1];[a1]showwaves=s=1920x1080:mode=cline:colors=green:draw=full:rate=25 [t1]; [vid1] [t1] overlay [vo]'
```

This is very useful to seek to accurate audio point by looking at a waveform in mpv player, by pressing `,` `.`
