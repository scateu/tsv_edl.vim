# TSV EDL Plugin

This plugin provides helpful commands for editing a TSV EDL file, and allows you to control mpv over a socket while editing a TSV EDL file.

## Commands

* `edl_play_current_line` Play just the current line, at the cursor's position
* `edl_toggle_play` Start playing at the cursor's position
* `edl_break_line` Split the current line at the cursor's position
* `edl_join_selected_lines` For any selections, combine the lines into a single line
* `edl_reject` Reject (xxx out) the current line/lines selected
* `edl_toggle` Toggle between EDL and xxx. toggle --- to EDL

## Keybindings

This plugin doesn't define keybindings. It's recommended to put something similar to the following in your `bindings.json`:

```json
{
	"Alt-Tab": "command:edl_play_current_line",
	"Alt- ": "command:edl_toggle_play",
	"Alt-\\": "command:edl_break_line",
	"Alt-j": "command:edl_join_selected_lines",
	"Alt-Delete": "command:edl_reject",
	"Shift-Alt-Delete": "command:edl_toggle",
}
```
