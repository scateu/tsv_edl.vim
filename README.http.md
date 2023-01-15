# Online video

```
EDL	00:00:00,000	00:00:10,000	| https://www.bilibili.com/video/BV1Ed4y1b7bm?p=1 |	.....
EDL	00:21:54,000	00:21:59,000	| https://www.bilibili.com/video/BV1Ed4y1b7bm?p=1 |	.....
EDL	00:31:54,000	00:31:59,000	| https://www.bilibili.com/video/BV1Ed4y1b7bm?p=1 |	.....
EDL	00:41:54,000	00:41:59,000	| https://www.bilibili.com/video/BV1Ed4y1b7bm?p=1 |	.....

EDL	00:00:00,417	00:00:09,541	| https://www.bilibili.com/video/BV128411G7Xw/ |	0.00s. 3.04s. 

EDL	00:57:06,139	00:57:13,362	| https://www.youtube.com/watch?v=MKWZB_kEwUo |	0.02s.;7.22s. .... future
EDL	00:26:09,014	00:26:19,034	| https://www.bilibili.com/video/BV128411G7Xw/ |	0.02s.
EDL	00:00:01,000	00:00:20,633	| https://twitter.com/i/status/1601846128877576193 |	 ......
```

`tsv_edl.vim` will notice the filename starts with 'http'.

 - `\ SPACE` (not in IPC mode) will play each line (from start to end) one by one. 
 - `\\` then up/down arrow works same as before
 - `gi`  `go` works as before. however, as in youtube and twitter videos, the media file name is truncated. 

# TODO

 - [X] tsv2roughcut needs to download the portion/full of the http(s) media, and render them. but it shouldn't be too painful to do by hand.
 - [-] `gi`  `go` works as before. however, as in youtube and twitter videos, the media file name is truncated. 


# Copy URL with timestamp and make an EDL line

Suppose you paste the following two lines into vim. You can get this by right-click on the youtube or bilibili web player.

```
https://youtu.be/aJOPr2S0HXg?t=69
https://youtu.be/aJOPr2S0HXg?t=72
```

Then place cursor at the first line, then press `J`. It will become:

```
EDL	00:01:09,000	00:01:12,000	| https://youtu.be/aJOPr2S0HXg |	3.0 secs. 
```
## Notes about bilibili

Now `tsv_edl.vim` can handle the following URLs correctly,

```
https://www.bilibili.com/video/BV1sQ4y1B7wY?t=0.9
https://www.bilibili.com/video/BV1sQ4y1B7wY?t=100.0
```

and 


```
https://www.bilibili.com/video/BV1sQ4y1B7wY?t=2.3&p=6
https://www.bilibili.com/video/BV1sQ4y1B7wY?t=102.3&p=6
```


However, please be advised -- due to bug of `youtube-dl`/`yt-dlp`, sometime you have to add `&p=1` at the first episode of a bilibili list. Otherwise `youtube-dl` won't work.

# TIPS: Download Bilibili auto-generated subtitle

- <https://greasyfork.org/zh-TW/scripts/378513-bilibili-cc%E5%AD%97%E5%B9%95%E5%B7%A5%E5%85%B7>


# TIPS:

You can easily change clipname to URL in vim like so:

```
:%s,| .* |,| https://www.c-span.org/video/?159079-1/president-jiang-interview |,
```

# TIPS: duration unknown

You may set a significantly larger duration if it's unknown while you want to combine two videos. FFmpeg will tolerate it. It's especially useful when using twitter.

```
EDL	00:00:00,000	00:02:30,000	| https://video.twimg.com/ext_tw_video/xxxxxxxxxxxxxxxxxxx/pu/vid/480x848/xxxxxxxxxxxxxxxx.mp4?tag=12 |	[ VIDEO 10*60 secs  ]
EDL	00:00:00,000	00:01:38,000	| https://video.twimg.com/ext_tw_video/xxxxxxxxxxxxxxxxxxx/pu/vid/480x848/yyyyyyyyyyyyyyyy.mp4?tag=12 |	[ VIDEO 10*60 secs  ]
```

By the way, when a twitter link has multiple videos, you can manually get the URLs first.

```bash
$ yt-dlp -g https://twitter.com/xxxxxxxx/status/yyyyyyyyyyyyyyyyyyy/video/2
https://video.twimg.com/ext_tw_video/1111111111111111111/pu/vid/480x848/aaaaaaaaaaaaaaaa.mp4?tag=12
https://video.twimg.com/ext_tw_video/1222222222222222222/pu/vid/480x848/bbbbbbbbbbbbbbbb.mp4?tag=12
```


# Youtube

Don't worry. I've handled this in `tsv2roughtcut.py`.


## Youtube download a portion

```
$ youtube-dl --get-url --youtube-skip-dash-manifest "https://www.youtube.com/watch?v=UxWuy6zSWOA"
https://rr3---sn-oguelnzl.googlevideo.com/videoplayback?expire=1670596230&ei=JfKSY4mTN6Kxigbr67vwCQ&ip=202.182.105.114&id=o-ACGz_jL-o5wuwMpgOmwFrXOK7jxcPykJKob5J99OZ-9D&itag=136&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278&source=youtube&requiressl=yes&mh=ve&mm=31%2C29&mn=sn-oguelnzl%2Csn-oguesndr&ms=au%2Crdu&mv=m&mvi=3&pl=24&gcr=jp&initcwndbps=1333750&vprv=1&mime=video%2Fmp4&ns=wPf3BtPCRZf1cF0LLngcaDkJ&gir=yes&clen=1265600061&otfp=1&dur=6490.249&lmt=1624129867558506&mt=1670574291&fvip=3&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=6216224&n=wjxP4kp-CTUM2uN5c&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cgcr%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cotfp%2Cdur%2Clmt&sig=AOq0QJ8wRgIhAJfXcpAhTjmtU_Lbk4NwczKrWYxSxj8zFqFSOoDuQFFQAiEAhWEECaLBlVGKA9ZDRUtSjSKIq2pQrtSf-gxgFnvGqyI%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIgThtalb7xvhLkIMPGcizAK3j-2saH108gJa34HNzP2l4CIQCNH36X2prTUxaDmxREpdtVfiWUB2ecupSxCi4aCF11rg%3D%3D
https://rr3---sn-oguelnzl.googlevideo.com/videoplayback?expire=1670596230&ei=JfKSY4mTN6Kxigbr67vwCQ&ip=202.182.105.114&id=o-ACGz_jL-o5wuwMpgOmwFrXOK7jxcPykJKob5J99OZ-9D&itag=140&source=youtube&requiressl=yes&mh=ve&mm=31%2C29&mn=sn-oguelnzl%2Csn-oguesndr&ms=au%2Crdu&mv=m&mvi=3&pl=24&gcr=jp&initcwndbps=1333750&vprv=1&mime=audio%2Fmp4&ns=wPf3BtPCRZf1cF0LLngcaDkJ&gir=yes&clen=105040576&otfp=1&dur=6490.394&lmt=1624130253419646&mt=1670574291&fvip=3&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=6211224&n=wjxP4kp-CTUM2uN5c&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cgcr%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cotfp%2Cdur%2Clmt&sig=AOq0QJ8wRgIhAJAMguVNzfE11WIc5x-2Vu6QBnf0bI2SWrqcIfA8bbUXAiEA3WngVAqB6ejCvVGxWSJ2tpLIbZ9Wkgscf5zyJdropVM%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIgThtalb7xvhLkIMPGcizAK3j-2saH108gJa34HNzP2l4CIQCNH36X2prTUxaDmxREpdtVfiWUB2ecupSxCi4aCF11rg%3D%3D

$ ffmpeg -ss 01:43:07 -to 01:43:50 -i "https://rr3---sn-oguelnzl.googlevideo.com/videoplayback?expire=1670596230&ei=JfKSY4mTN6Kxigbr67vwCQ&ip=202.182.105.114&id=o-ACGz_jL-o5wuwMpgOmwFrXOK7jxcPykJKob5J99OZ-9D&itag=136&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278&source=youtube&requiressl=yes&mh=ve&mm=31%2C29&mn=sn-oguelnzl%2Csn-oguesndr&ms=au%2Crdu&mv=m&mvi=3&pl=24&gcr=jp&initcwndbps=1333750&vprv=1&mime=video%2Fmp4&ns=wPf3BtPCRZf1cF0LLngcaDkJ&gir=yes&clen=1265600061&otfp=1&dur=6490.249&lmt=1624129867558506&mt=1670574291&fvip=3&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=6216224&n=wjxP4kp-CTUM2uN5c&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cgcr%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cotfp%2Cdur%2Clmt&sig=AOq0QJ8wRgIhAJfXcpAhTjmtU_Lbk4NwczKrWYxSxj8zFqFSOoDuQFFQAiEAhWEECaLBlVGKA9ZDRUtSjSKIq2pQrtSf-gxgFnvGqyI%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIgThtalb7xvhLkIMPGcizAK3j-2saH108gJa34HNzP2l4CIQCNH36X2prTUxaDmxREpdtVfiWUB2ecupSxCi4aCF11rg%3D%3D" -ss 01:43:07 -to 01:43:50 -i "https://rr3---sn-oguelnzl.googlevideo.com/videoplayback?expire=1670596230&ei=JfKSY4mTN6Kxigbr67vwCQ&ip=202.182.105.114&id=o-ACGz_jL-o5wuwMpgOmwFrXOK7jxcPykJKob5J99OZ-9D&itag=140&source=youtube&requiressl=yes&mh=ve&mm=31%2C29&mn=sn-oguelnzl%2Csn-oguesndr&ms=au%2Crdu&mv=m&mvi=3&pl=24&gcr=jp&initcwndbps=1333750&vprv=1&mime=audio%2Fmp4&ns=wPf3BtPCRZf1cF0LLngcaDkJ&gir=yes&clen=105040576&otfp=1&dur=6490.394&lmt=1624130253419646&mt=1670574291&fvip=3&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=6211224&n=wjxP4kp-CTUM2uN5c&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cgcr%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cotfp%2Cdur%2Clmt&sig=AOq0QJ8wRgIhAJAMguVNzfE11WIc5x-2Vu6QBnf0bI2SWrqcIfA8bbUXAiEA3WngVAqB6ejCvVGxWSJ2tpLIbZ9Wkgscf5zyJdropVM%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIgThtalb7xvhLkIMPGcizAK3j-2saH108gJa34HNzP2l4CIQCNH36X2prTUxaDmxREpdtVfiWUB2ecupSxCi4aCF11rg%3D%3D"  -c copy a.mkv

```


 - see <https://superuser.com/questions/1661048/how-to-download-a-portion-of-a-youtube-video>


or use `yt-dlp` <https://github.com/yt-dlp/yt-dlp>

> Download time range: Videos can be downloaded partially based on either timestamps or chapters using --download-sections

```
yt-dlp --download-sections "*10:00-11:00" https://www.youtube.com/watch?v=PdMp_RjO7CA
```

# TIPS: Clear DNS cache on macOS

if something goes wrong, like, you dial up a VPN just now. Clear DNS cache may helps:

```
dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```
