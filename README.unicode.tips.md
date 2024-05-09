# Unicode tips

Some transcription service will spit out unicode zero width space characters, which looks like

    <200b><200c><200b><200c><200b><200c><200b><200c><200b><200c><200b><200c><200b><200c><200b><200c><200b><200c><200b><200c><200b><200c>

The following `sed` command will fix it:

    gsed -i 's/\xe2\x80\x8b//g' *.srt  #<200b>
    gsed -i 's/\xe2\x80\x8c//g' *.srt  #<200c>
