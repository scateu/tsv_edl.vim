# Sort

You may open tsv file in Numbers, Google Docs, or Excel, and add several useful columns, which makes the layout to be:

```
EDL	Record In	Record Out	Clipname	Subtitle	Speaker Topic	B Roll	Before	After
```

Later you may do a multi-column sort by the following priority:

1. Topic
2. Speaker
3. Record In


Which makes life way easier.


# Tips: Davinci Resolve workflow - All interviews

1. Add all interviews into one single timeline.
2. Render it as a single long video file.
3. Transcribe it, and export the srt file. (Studio version of Davinci Resolve has a local model, which works pretty well. Just remember to assign that start timecode of this timeline to 00:00:00,000)
4. `srt2tsv` and edit, edit, edit ...
5. `V` highlight and `x` export via `tsv2fcpxml`. Remember to change the FPS value accordingly.
6. [The trick!] Import this xml file into Davinci Resolve will make it link to **the single long video file** in Step 2. You may simply rename **that single long video file** before import to Davinci Resolve (and after `tsv2fcpxml`, because `tsv2fcpxml` will search fot the path the video file.)  Then Davinci Resolve will not find **that single long video file** and choose your timeline (from Step 1) as the second best option.
7. Select all clips in the new timeline, do `decompose in place` from Davinci Resolve. Ta-da!
