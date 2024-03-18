# Record Voice Over

NOTE: `sox` needed. `ffmpeg` will cause bad audio on macOS; `brew install sox` or `sudo apt install sox`

First write down some lines that you want to read, like

```
Oh, captain my captain
In this film, you may find the director is not quite himself
...
```

then, on the first line, press `gr` (only left hand needed)

`sox -D VoiceOver_2024-03-18-11h34m52s.wav` will be invoked.

You speak into the default microphone of your system, then press `Ctrl-C` to stop it.

then the file will become:

```
EDL 00:00:00,000    00:00:10,000    | VoiceOver_2024-03-18-11h34m52s |  Oh, captain my captain
In this film, you may find the director is not quite himself
```

Next, you press `ge` to read back the real length of this wav file. It becomes:

```
EDL 00:00:00,000    00:00:03,313    | VoiceOver_2024-03-18-11h34m52s |  Oh, captain my captain
In this film, you may find the director is not quite himself
```

You may fine tune the in/out point with `Tab` and `gi` `go` `Space`.

Next, you record the next line.
```
EDL 00:00:00,000    00:00:03,313    | VoiceOver_2024-03-18-11h34m52s |  Oh, captain my captain
EDL 00:00:01,033    00:00:08,341    | VoiceOver_2024-03-18-11h34m52s |  In this film, you may find the director is not quite himself
```


You can add a film clip that you just described, as B roll, with `gb`:


```
EDL 00:01:23,456    00:01:33,455    | Dead Poets Society | [B]
EDL 00:00:00,000    00:00:03,313    | VoiceOver_2024-03-18-11h34m52s |  Oh, captain my captain
EDL 00:03:03,123    00:03:04,455    | Some other shitty film | [B]
EDL 00:00:01,033    00:00:08,341    | VoiceOver_2024-03-18-11h34m52s |  In this film, you may find the director is not quite himself
```


If you are not satisfied with your acting, you can do `gr` again on the line, previous takes will be reserved:

```
EDL 00:01:23,456    00:01:33,455    | Dead Poets Society | [B]
EDL 00:00:00,000    00:00:03,313    | VoiceOver_2024-03-18-11h37m03s |  Oh, captain my captain
xxx 00:00:00,000    00:00:03,313    | VoiceOver_2024-03-18-11h34m52s |  Oh, captain my captain
EDL 00:03:03,123    00:03:04,455    | Some other shitty film | [B]
EDL 00:00:01,033    00:00:08,341    | VoiceOver_2024-03-18-11h35m12s |  In this film, you may find the director is not quite himself
```


# Voice Over 录音


先写几行台词，在每一行上按gr开始录音，Ctrl-c停止，自动保存到当前目录，命名为VoiceOver_yyyymmddhhmmss.wav；
然后这一行变成

    EDL 00:00:00,000 00:00:10,000 | VoiceOver_yyyymmddhhmmss |  台词台词台词

按ge更新录音文件长度，

    EDL 00:00:00,000 00:00:04,230 | VoiceOver_yyyymmddhhmmss |  台词台词台词

按gb把这行变成[B] b轨，

    EDL 00:00:00,000 00:00:04,230 | VoiceOver_yyyymmddhhmmss |  [B]台词台词台词
    EDL 01:23:45,000 01:23:55,123 | 奥本海默 | 啊该死的华生

就可以叠到下一行的电影上，形成旁白了
