## INSTALLATION

    mkdir -p ~/.vim/pack/plugins/start
    cd ~/.vim/pack/plugins/start
    git clone https://github.com/scateu/tsv_edl.vim

    make install-utils 
    # tsv2edl srt2tsv_all audio2srtvideo tsv2srt tsv2srt_py

## SRT -> TSV

    cd /path/to/srt/
    srt2tsv_all

or: in vim, `:!srt2tsv_all`

or: in vim, `V` to mark a region, and press `:` then type `!srt2tsv`, 
to filter this region through the corresponding util.

## Cherry-pick

    touch selection1.tsv
    vim -p selection1.tsv movie1.tsv podcast1.tsv podcast2.tsv movie2.tsv  #target has to be the first tab

On media files tab, press 'Enter' will:
 - Copy this line to the end of `tab 1`
 - Mark this line as used `---`
 - Move to the next line 

Press `Backspace` or `Delete` will:
 - Mark this line as rejected, mark `xxx` at the head of this line
 - Move to the next line

Press `Space` will:
 - Continous play lines start with `EDL`

<del>
 - Add a newline at the end of `tab 1`
 - Go back to current position
</del>

Press `Tab` will:
 - Invoke `ffplay` the `*clipname*.!(tsv|srt|txt)'` in current directory, starting from time `record_in`
 - Press `q` to stop
 - Will try to infer a playback timecode according to cursor position
    - `Shift-Tab` will bypass guessing position

Press `J` will:
 - Merge the next line. Join those two timecode

Press `|` on a character will:
 - Split this line into two. 
 - Will guess out a new timecode in break point, by words length

Press `Shift-Left` or `Shift-Right` will:
 - Shift `Record In` timecode of this line to 1 sec left
 - Shift `Record Out` timecode of previous line to 1 sec left
 - This function is pretty much like 'Roll' operation in Davinci Resolve

Press `g0` will:
 - Go to the head of subtities.

Press `g9` will:
 - Go to `record_in` timecode. You may like this keybinding with `C-a` `C-x` to increase/decrease number.

*NOTE*: `:mksession` to save a `Session.vim` to the current folder may be very useful before reloading this session with `vim -S`.

## Assemble a timeline

(You may want to change the `FPS` value in `utils/tsv2edl.py`)

    grep EDL selection.tsv | tsv2edl > selection.edl

or with Makefile, you can do `:make` or `:make selection2.edl` or `:make %[Tab Key] [backspace..].edl` within vim.

```makefile
selection.edl: selection.tsv
	grep EDL $< | tsv2edl > $@
```

```makefile
%.edl: %.tsv
	grep EDL $< | tsv2edl > $@
```

Then import the .edl file into Davinci Resolve (Cmd-Shift-i) / Adobe Premiere. 
Or find your way to convert it to .fcpxml

*NOTE*: the starting TC of a source clip needs to be '01:00:00:00'. You may shift the clips in Davinci Resolve, or you change the `utils/tsv2edl.py` accordingly.

*NOTE*: If Davinci Resolve matches a wrong clip, you may create a new bin contains the only clip. Then you import EDL, click done, and in the next window, choose the only new bin.

*NOTE*: If the source slip is a pure audio file, you may create a timeline, lay down the audio file and rename the timeline exactly the same as the clipname. Starting timecode must match.

Or ...

## Convert MP3/Audio to Dummy video with SRT

Due to the limitation of Davinci Resolve that EDL file cannot be reconstructed into a timeline refering to pure audio file, 
a helper bash script is prepared in `utils/audio2srtvideo.sh`

```
audio2srtvideo "Some podcast E01.mp3"
```

will yield a `Some podcast E01.mkv`

*NOTE*: You may want to move those mkv files into a subdirectory named, for example, `mkvs`, so that `Tab` key `ffplay` will not be confused.

## See Also

 - sc-im: spreadsheet in terminal
 - http://podcasts.bluepill.life/ a firefox podcast addon, so convinient to download mp3 files
 - REFERENCE 
	- Python vs Vimscript: https://gist.github.com/yegappan/16d964a37ead0979b05e655aa036cad0
	- Vimscript cheatsheet: https://devhints.io/vimscript

## TODOs

 - [X] srt handling: fill in the caps. extend ~~the first to 00:00:00.00~~, and the end of every following clips to the next start TC, using a threshold of 0.3sec
 - [X] edl2srt: convert back.
 - [X] Tab: deduce a location regarding the start timecode, so that when you start in the middle of a long line won't make you wait for long time.
 - [ ] Gap: EDLSPACE?
 - [ ] When there's only one tab, `Enter` and `Space` cease to work. 

 ## Know bugs
 - macOS: `set shell=/bin/bash` otherwise, in zsh, error will occur
