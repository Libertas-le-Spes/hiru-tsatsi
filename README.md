# Omastart

An Omarchy bar widget that asks, right when the shell starts, whether you
want to launch your daily work apps — each one landing on its own
configured workspace, no clicking through window after window.

![Omastart panel](preview.png)

## Install

```sh
omarchy plugin add https://github.com/diegovrocha/omarchy-omastart.git --enable
```

## Usage

Click the lightning bolt icon in the bar (⚡ filled once you have apps
configured, outline while empty) to open the panel any time. It also opens
itself automatically once per shell session, right after Omarchy starts.

- **Start work apps** — launches every configured app into its workspace.
- **Add an app** — inside a workspace block, fill in a **Name** (just a
  label) and a **Command** (a real shell command) and press **+**.

  ![Adding an app to a workspace](docs/add-app.png)

- **Remove an app or workspace** — the ✕ next to each row.
- **Add a workspace** — the field and button at the bottom of the panel.

State is saved to `~/.local/state/omarchy/settings/omastart.json` and
survives plugin updates.

### Command examples

The **Command** field takes anything you'd normally run in a terminal to
open the app. A few examples:

| App | Command |
|---|---|
| Chromium | `chromium` |
| VS Code | `code` |
| A web app | `omarchy-launch-webapp https://web.whatsapp.com/` |
| Herdr | `omarchy-launch-terminal-herdr` |
| An app needing a specific GTK theme | `env GTK_THEME=Adwaita:light dbeaver` |

## Dependencies

None beyond Omarchy/Hyprland itself. Launching uses `hyprctl dispatch`
(built into Hyprland) — no extra packages to install. Whatever you put in
a workspace's **Command** field needs to already be installed, same as
running it in a terminal.

## Known limitation: single-instance apps

Hyprland's `[workspace N silent]` exec tag only attaches to the process
`hyprctl dispatch exec` actually spawns. For an app that reuses an already
running instance instead of starting a new one — a browser opening a
`--app=` webapp window in an already-open Chromium, VS Code or DBeaver
handing the request to their existing instance over IPC, an Electron app
that stayed alive in the tray after its window was closed — the real
window is created by that pre-existing process, not the one Hyprland just
tagged, so the window lands on whatever workspace you're currently on
instead of the one you configured.

Omastart can't fix this from inside the plugin: the exec tag is a
Hyprland mechanism, and there's no signal telling the launcher an
invocation was silently handed off to an existing instance. If you hit
this for one of your apps, pin it with a persistent window rule keyed on
window class instead, e.g. in `~/.config/hypr/hyprland.lua`:

```lua
o.window("code", { workspace = "3 silent" })
```

Find the class with `hyprctl clients` while the app is open.

## Language

The panel's text follows the machine's configured language
(`Qt.locale()`), not whatever language you happen to be using elsewhere —
currently ships with `pt_BR` and an English default/fallback for every
other locale. See `Strings.js` to add more.

## Remove

```sh
omarchy plugin remove io.github.diegovrocha.omastart
```

Your saved workspaces/apps stay at
`~/.local/state/omarchy/settings/omastart.json` — delete that file too if
you want a clean slate.

## Development

```sh
omarchy plugin validate .
```
