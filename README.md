# Omastart

An Omarchy bar widget for Hiru Tsatsi: one click starts your daily work
apps, each one landing on its own configured workspace, and the panel next
to the icon is where you edit them.

Omastart was created by Diêgo Vieira
([diegovrocha/omarchy-omastart](https://github.com/diegovrocha/omarchy-omastart))
and is MIT licensed; see `LICENSE`. This copy has grown into Hiru Tsatsi and
is maintained by Kabelo Mosiane.

![Omastart panel](preview.png)

## Install

```sh
omarchy plugin add https://github.com/Libertas-le-Spes/hiru-tsatsi.git --enable
~/.config/omarchy/plugins/kayu.hiru-tsatsi/install.sh
```

## Usage

Click the lightning bolt icon in the bar (⚡ filled once you have apps
configured, outline while empty) to open the panel any time. At login,
Hiru Tsatsi asks with a notification whether to start your work apps.

- **Start work apps** — launches every configured app that isn't already
  open, all at once, and moves each window to its workspace as it appears.
  Apps that are already open are moved instead of opened a second time.
- **Add an app** — inside a workspace block, fill in a **Name** (just a
  label) and a **Command** (a real shell command) and press **+**. If the
  app is open, its window is recognised at once; otherwise the first time
  Hiru Tsatsi starts it.
- **Remove an app or workspace** — the ✕ next to each row.
- **Add a workspace** — choose its number and name at the bottom of the
  panel.

Every change goes through Hiru Tsatsi (`hiru-tsatsi add-app`, `add-workspace`
and so on), so the panel holds no rules of its own. The list is
`~/.config/hiru-tsatsi/apps.json`, and **Start work apps** runs
`hiru-tsatsi start` (see `backend/README.md`).

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

Hiru Tsatsi, installed with `./install.sh` (Python 3.10 or newer, nothing
else). Whatever you put in
a workspace's **Command** field needs to already be installed, same as
running it in a terminal.

## How windows are matched

Hyprland's `[workspace N silent]` exec tag only reaches the process
`hyprctl dispatch exec` spawns. An app that hands the request to a copy
already running — a `--app=` webapp in an open Chromium, a second Rider
project, Steam sitting in the tray — opens its window wherever you are.
So each app remembers its window: the start of its class, or of its title
where several windows share a class (two Rider projects, for example).
After launching, Hiru Tsatsi watches for a minute and moves each matching
window to its workspace.

## Language

The panel's text follows the machine's configured language
(`Qt.locale()`), not whatever language you happen to be using elsewhere —
currently ships with `pt_BR` and an English default/fallback for every
other locale. See `Strings.js` to add more.

## Remove

```sh
omarchy plugin remove kayu.hiru-tsatsi
```

Your saved workspaces/apps stay at
`~/.config/hiru-tsatsi/apps.json` — delete that file too if
you want a clean slate.

## Development

```sh
omarchy plugin validate .
```
