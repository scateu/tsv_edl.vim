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

first, you remap `Enter` key to 

```
:nmap <enter> <space>gojgi<space>
```

then, you manually add to the first sentence.

```
EDL 00:00:00,000    00:00:00,000    | filename |    JAD: Yeah.
```

after that, you press `\\` on this line, to bring `mpv` up.

Press spacebar to play.

Press `Enter` when this sentence is read. It will update the out time and move cursor to the next line, and insert 'in' time.

You just need to press 'Enter' on and on.
