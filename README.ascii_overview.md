<details markdown="1"><summary>Click here to see full ASCII diagram</summary>

```
media -- [scenecut_preview]  detect scene cut and slice into tsv
         [    audiocut    ]  detect scene cut by audio silence
                       |
		       V
.srt --- [srt2tsv] --> .tsv file
                       |
		       V
		      Vim: proofread ---- [tsv2srt] ------> .srt file 
		       |                                       \- [audio2srtvideo]
		       |                                                \---> .mkv (with TC)
		       V
		      Vim: add notes and '* Section' '** Subsection'
		       |
		       V
		      Vim: Tab    (Preview)
		       |   Enter  (Select)
		       |   Delete (Reject)
		       |   cherry-pick / re-arrange
		       V 
	       Google Spreadsheet: Invite your editor friends to edit
		       |
		       |
		       \----> selected .tsv file 
		                |       \
				|	 \----[tsv2fcpxml] -> .fcpxml --> FCPX/DaVinci 
				|	  \
			        |     [tsv2edl] --> .edl file
				|                         \
				v  	                   \--> DaVinci Resolve: fine tuning
			 [tsv2roughcut]	                              \
							               \
							                \---> Production
```

</details>
