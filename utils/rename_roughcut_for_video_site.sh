#!/bin/bash

if [[ $OSTYPE == 'darwin'* ]]; then
  SED=gsed
else
  SED=sed
fi

mv roughcut.mp3 "$1.mp3"
mv roughcut.srt "$1.srt"
audio2srtvideo "$1.mp3"

${SED} -r '/^[0-9]+$/{N;d};/^$/d' "$1.srt" | grep -v "\[ SPACE" > "$1.txt"
#${SED} -r '/^[0-9]+$/{N;d}' "$1.srt" | grep -v "\[ SPACE" | grep . > "$1.txt"
# sed -r  '/^[0-9]+$/,+1d'

echo "$1.txt" generated.
