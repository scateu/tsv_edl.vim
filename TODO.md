# TODOs

 - [ ] mpv ipc mode: Tab should stop at Record Out.
 - [ ] media path support. or a very fancy `ln -s` helper?
 - [ ] tesseract OCR on existing burn-in subtitle
 - [ ] replace 'jq' 'socat' with python standard library, maybe with [this](https://github.com/iwalton3/python-mpv-jsonipc)
 - [X] Gap: EDLSPACE?  `go`
 - [X] When there's only one tab, `Enter` should cease to work. 
 - [X] Tab/Space key on a visual region. render the region into a media file
 - [X] tsv2srt -reflow: reassign the timestamp of each srt block. generate a srt for the rendered region
 - [X] mpv --input-ipc-server 
 - [X] bug: macOS: `set shell=/bin/bash` otherwise, in zsh, error will occur
 - [X] `set fdm=expr` is very slow. need to switch to `manual` or add a cache
 - [X] doesn't work on vim 9
 - [ ] fcpxml2tsv
 - [ ] robustness of tsv2fcpxml

 - [X] sometime the final product starts with a black screen

>  The following words are from losslesscut project
>  '-i', filePath,
> '-ss', '0', // If we don't do this, the output seems to start with an empty black after merging with the encoded part
>  '-t', (cutTo - cutFrom).toFixed(5),
