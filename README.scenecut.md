# scenecut

```
scenecut_preview movie.mkv
```
will detect scene change (thanks to ffmpeg) and generate `movie_scenecut.tsv` with a folder containing all snapshots.

# audiocut

```
audiocut movie.mkv
```
will cut by detecting silence and generate `movie_audiocut.tsv`

# TIPS: split srt into chapters

you may concatenate scenecut/audiocut with origin subtitles. `sort` command will do magic.

```
cat movie_scenecut.tsv movie.tsv | sort > movie1.tsv
```
After sorting, you may replace those scenecut lines with empty ones. It will be extremely useful as a scene indication.
