# TSV EDL Plugin

This plugin provides helpful commands for editing a TSV EDL file, and allows you to control mpv over a socket while editing a TSV EDL file.

## Commands

* `edl_play_current_line`
* `edl_toggle_play`

## Keybindings

This plugin doesn't define keybindings. It's recommended to put something similar to the following in your `bindings.json`:

```json
{
	"Alt-Tab": "command:edl_play_current_line",
	"Alt- ": "command:edl_toggle_play",
	"Alt-\\": "command:edl_break_line",
}
```
