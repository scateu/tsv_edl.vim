# scenecut_preview

 - Workflow receives current "movie files" in "Finder"
 - Image: screenshot
 - Color: 


 - Shell: /bin/bash   Pass input: as arguments


```
export LANG=en_US.UTF-8
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
if [[ -d "$@" ]]; then
	echo "Nein."
elif [[ -f "$@" ]]; then
    cd "$(dirname "$@")"
	/usr/local/bin/scenecut_preview "$(basename "$@")" 
fi

```

------------------------------

Quick Action location: ~/Library/Services

# Application: tsv2roughcut

 - open Automator.app, choose 'Application' type.
 - drag 'Run AppleScript' into flow
 - paste the following line in
 
```applescript
tell application "Finder" to set currentDir to (target of front Finder window) as text
do shell script "export LANG=en_US.UTF-8; export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin; cd " & (quoted form of POSIX path of currentDir) & "; pbpaste | /usr/local/bin/tsv2roughcut && echo '完了' | say -v Ting-Ting"
# https://stackoverflow.com/questions/12129989/getting-finders-current-directory-in-applescript-stored-as-application
#say "Hooray, rendering done." using "Samantha"
#say "完了" using "Ting-Ting"
```

# Application: srt2tsv_all

 - save it in /Application/tsv_edl/ folder. name it as 'tsv2roughcut'
 - Drag it to Finder toolbar, with 'Cmd' key pressed

Then, make a new 'srt2tsv_all' using the following line:

```applescript
tell application "Finder" to set currentDir to (target of front Finder window) as text
do shell script "export LANG=en_US.UTF-8; export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin; cd " & (quoted form of POSIX path of currentDir) & ";/usr/local/bin/srt2tsv -a"
```

(You may steal an icon with `Cmd-i`, `Cmd-i` on another application, `Cmd-C` `Cmd-V` on icons.) [[Ref]](https://developer.apple.com/library/archive/technotes/tn2065/_index.html)

