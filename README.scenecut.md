# scenecut

```
scenecut movie.mkv
```
will detect scene change (thanks to ffmpeg) and generate `movie_scenecut.tsv` with a folder contains all snapshots.

# audiocut

```
audiocut movie.mkv
```
will cut by detecting silence. generate `movie_audiocut.tsv`

# TIPS: split srt into chapters

you may concatenate scenecut/audiocut with origin subtitles, with `sort` command will do magic.

```
cat movie_scenecut.tsv movie.tsv | sort > movie1.tsv
```
