# macOS shortcuts

In the latest version of macOS, Workflow.app is deprecated and replaced by Shortcuts.app.

Since apple has to audit my code before this shortcut can be shared, you might add it manually.


## srt2tsv
 - Click 'Quick Actions' on the left sidebar, then '+' to make a new one.
 - Receive 'Files' input from 'Quick Actions'.  If there's no input: 'Continue'
 - Run Shell Script

```bash
export LANG=en_US.UTF-8
export PATH=/opt/homebrew/bin/:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

for item in "$@"
do
    if [[ -d "$item" ]]; then
	echo "Nein."
elif [[ -f "$item" ]]; then
    cd "$(dirname "$item")"
	/usr/local/bin/srt2tsv "$(basename "$item")"
fi
done
```

 - Shell: "bash"
 - Input: "Shortcut Input"
 - Pass Input: "as arguments"
 - Details:
   - [X] Use as Quick Action
    - [X] Finder
    - [X] Services Menu

To use it:
 - right click on one or multiple `.srt` file > quick actions > `srt2tsv`

## srt2tsv\_all

 - New
 - Receive 'Media' input from 'Quick Actions', if there's no input: 'Continue'
 - Run AppleScript with 'Shortcut input'

```applescript
tell application "Finder" to set currentDir to (target of front Finder window) as text
do shell script "export LANG=en_US.UTF-8; export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin; cd " & (quoted form of POSIX path of currentDir) & ";/usr/local/bin/srt2tsv -a"
```

 - Details:
    - [X] Pin in Menu Bar
    - [ ] Use as Quick Action
      - [ ] Finder

To use it:
 - Navigate to the Finder folder with `.srt` files
 - click the 'Shortcuts' button on the top menu of macOS, then click 'srt2tsv\_all'

## scenecut\_preview

 - Receive Media input from Quick Actions. If there's no input: 'Continue'
 - Run Shell Script

```bash
export LANG=en_US.UTF-8
export PATH=/opt/homebrew/bin/:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
if [[ -d "$@" ]]; then
	echo "Nein."
elif [[ -f "$@" ]]; then
    cd "$(dirname "$@")"
	/usr/local/bin/scenecut_preview "$(basename "$@")" 
fi
```
 - Shell: bash
 - Input: 'Shortcut Input'
 - Pass Input: 'as arguments'
 - Details
   - [X] Use as Quick Action
    - [X] Finder

To use it:
 - Right click on the footage file
 - Quick Actions > "scenecut\_preview"

## tsv2fcpxml 

 - Receive 'Files' input from 'Quick Actions'.  If there's no input: 'Continue'
 - Run Shell Script

```bash
export LANG=en_US.UTF-8
export PATH=/opt/homebrew/bin/:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
if [[ -d "$@" ]]; then
	echo "Nein."
elif [[ -f "$@" ]]; then
    cd "$(dirname "$@")"
	cat "$(basename "$@")"  | /usr/local/bin/tsv2fcpxml > a.fcpxml
fi
```

 - Shell: "bash"
 - Input: "Shortcut Input"
 - Pass Input: "as arguments"
 - Details:
  - [X] Use as Quick Action
   - [X] Finder
   - [X] Services Menu

## tsv2roughtcut

 - Receive 'Files' input from 'Quick Actions'.  If there's no input: 'Continue'
 - Run Shell Script

```bash
export LANG=en_US.UTF-8
export PATH=/opt/homebrew/bin/:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
if [[ -d "$@" ]]; then
	echo "Nein."
elif [[ -f "$@" ]]; then
    cd "$(dirname "$@")"
	cat "$(basename "$@")"  | /usr/local/bin/tsv2roughcut
fi
```
 - Shell: "bash"
 - Input: "Shortcut Input"
 - Pass Input: "as arguments"
 - Details:
  - [X] Use as Quick Action
   - [X] Finder
## tsv2roughtcut from pasteboard

 - New
 - Receive 'Any' input from 'Nowhere'
 - Run Applescript with 'Shortcut input'

```applescript
tell application "Finder" to set currentDir to (target of front Finder window) as text
do shell script "export LANG=en_US.UTF-8; export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin; cd " & (quoted form of POSIX path of currentDir) & "; pbpaste | /usr/local/bin/tsv2roughcut && say yay"
```

 - [X] Pin in Menu Bar

To use it:
 - Copy 'EDL' lines to paste board, for example, from Numbers.app
 - Navigate to the Finder folder that contains footages
 - Click the 'Shortcuts' button on the top menu of macOS, then click 'tsv2roughtcut'

