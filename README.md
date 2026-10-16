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

- **Start work apps** — launches every configured app that isn't already
  open, all at once, and moves each window to its workspace as it appears.
  Apps that are already open are moved instead of opened a second time.
- **Add an app** — inside a workspace block, fill in a **Name** (just a
  label) and a **Command** (a real shell command) and press **+**. The
  **Window** list is filled in from the open window that best matches the
  command; pick a different one from the list if the guess is wrong. If the
  app isn't open yet, leave it empty: the window is learned the first time
  the app is started.

  ![Adding an app to a workspace](docs/add-app.png)

- **Remove an app or workspace** — the ✕ next to each row.
- **Add a workspace** — choose its number and name at the bottom of the
  panel.

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

## How windows are matched

Hyprland's `[workspace N silent]` exec tag only reaches the process
`hyprctl dispatch exec` spawns. An app that hands the request to a copy
already running — a `--app=` webapp in an open Chromium, a second Rider
project, Steam sitting in the tray — opens its window wherever you are.
So each app remembers its window: the start of its class, or of its title
where several windows share a class (two Rider projects, for example).
After launching, Omastart watches for a minute and moves each matching
window to its workspace.

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
