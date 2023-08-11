# What if you already have a transcription text file?


like:

```
JAD: Yeah.
SIMON: This is the first time anyone had ever seen that. 
JAD: Amazing. Amazing.
SIMON: And of course, if they took their headphones off, they rejoin our shared world hearing the din of the park and the city around them. But then when they put them back on, they’d be back in their own little world. Headphones off, collective reality. Headphones on, whatever personal reality, whatever mood they’ve chosen for themselves.
JAD: Oh my god.
SIMON: Totally, yeah. And maybe you can communicate this better than me because you’ve lived it, but like this was all so new. Like most of these people had probably never worn headphones before. They’ve never had stuff pumped directly into their ears. They’ve never listened to something outside before, short of transistor radio or maybe a boombox. And they’re now doing it altogether, but by themselves.
JAD: People don’t really understand what—a big deal the Walkman was. Like, remember when Steve Jobs did the iPhone and everybody’s like, “Oh my god, oh my god.”
SIMON: Yep, yep.
JAD: This was like that, times 1,000.
SIMON: You’d go that far?
```

<del>

 first, you remap `-` key to 

```
:nmap - :call tsv_edl#update_timeline_for_transcription()<cr>
```

ALREADY DONE.

</del>

You may also 

```
:set so=999
```

so that your working line stays in the middle of the screen.

Then, you manually add `EDL` head to the first sentence, and restart vim.

```
EDL 00:00:00,000    00:00:00,000    | filename |    JAD: Yeah.
```

after that, you press `\\` on this line, to bring `mpv` up.

Press spacebar to play.

Press `Enter` when this sentence is read. It will update the out time and move cursor to the next line, and insert 'in' time.

You just need to press 'Enter' on and on.


Finally, you may import the `srt` file into Davinci Resolve or other software to do fine-tuning. (caution: if the first srt line is not started at 00:00:00, you may add one. otherwise, it's not easy to import into Davinci Resolve timeline)


 - [X] FIXME: the time is not continuous. Maybe a function is needed.
 - [X] FIXME: come up with a good key to bind. `-`


## TIPS: break long sentence by the period sign

```
:g/\. /normal f.ll|
```
