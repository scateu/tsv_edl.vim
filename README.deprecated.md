### Details 
<details markdown="1"><summary>Click here to see full description of those keys</summary>
On media files tab, 

Press 'Enter' will:
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
 - Invoke `mpv`/`ffplay` the `*clipname*.!(tsv|srt|txt)'` in current directory, starting from time `record_in`
 - Press `q` to stop
 - Will try to infer a playback timecode according to cursor position
    - `Shift-Tab` will bypass position guessing

Press `J` will:
 - Merge with next line, join those two timecode

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

</details>

## tsv2edl: Assemble an EDL timeline

(You may want to change the `FPS` value in `utils/tsv2edl.py`)

```bash
grep EDL selection.tsv | tsv2edl > selection.edl
```

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
