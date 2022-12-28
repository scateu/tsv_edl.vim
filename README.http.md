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
