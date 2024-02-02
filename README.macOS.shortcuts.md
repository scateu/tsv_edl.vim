# macOS shortcuts

In the latest version of macOS, Workflow.app is deprecated and replaced by Shortcuts.app.

Since apple has to audit my code before this shortcut can be shared, you might add it manually.

![](https://raw.githubusercontent.com/scateu/tsv_edl.vim/main/screenshots/shortcuts.png)

## CAUTION: if srt2tsv doesn't work on Shortcuts but works from Terminal

(Mostly happens on macOS Sonoma.)

Probably you need to do the [following thing](https://discussions.apple.com/thread/255210852?sortBy=best):

>    Open Settings > Privacy & Security > Full Disk Access (or files and folders)
>
>    Toggle the Finder app on, or if you can't find it, click on the "+" button and add it
>
>    The Finder app should be in the following location:
>
>    /System/Library/CoreServices/Finder.app

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
    item_name=$(basename "$@")
    cd "$(dirname "$@")"
	cat "${item_name}" | /usr/local/bin/tsv2fcpxml > "${item_name%.*}.fcpxml"
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

## tsv2srt

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
    item_name=$(basename "$item")
    cd "$(dirname "$item")"
	 cat "${item_name}" | /usr/local/bin/tsv2srt > "${item_name%.*}.srt"
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

## (Experiemental) iCloud shared version

 - srt2tsv_all: https://www.icloud.com/shortcuts/28decb1d27d941bb9d0507827f7ad82e
 - tsv2roughtcut from pasteboard:  https://www.icloud.com/shortcuts/21cdd652f92c436b94bb328358dd9aa0
 - scenecut_preview: https://www.icloud.com/shortcuts/c7f40e4dce5349a39f7fde777ba976d8
 - tsv2srt:  https://www.icloud.com/shortcuts/2abc8459ce7b406dac0982fa558e0fb9
 - srt2tsv:  https://www.icloud.com/shortcuts/e9b149fb877443ccb8cae97af5d55759
 - tsv2fcpxml:   https://www.icloud.com/shortcuts/47af4a0500ce4e1fbaa47b5553f7f4b3
 - tsv2roughtcut: https://www.icloud.com/shortcuts/8c2d53aacfa348bb84c579a282db4942


