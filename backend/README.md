# Hiru Tsatsi

One key opens your work apps, each on the workspace you keep it on, on any Linux desktop.

Starting the day means opening the same apps and dragging each to its place. Doing it by hand is slow, and launchers that fire every command blindly open a second copy of whatever is already running, and leave windows wherever you happen to be. An app that hands the request to a copy already running (a web app inside an open browser, a second project in an open IDE, a game client in the tray) opens its window wherever you are, out of the launcher's reach.

So Hiru Tsatsi looks before it launches. Each app remembers its window: the start of its class, or of its title where several windows share a class. Apps already open are moved to their workspace instead of opened again; the rest all start at once, and each window is moved as it appears. Nobody has to know what a window class is: an app without one learns it from the first window that matches its command.

Only listing windows, moving them and launching differ between desktops, so each desktop is one class. On a desktop without one, Hiru Tsatsi starts nothing: apps opened without being put in their places would only leave the sorting to you.

## Use

```sh
./install.sh
```

It links the `hiru-tsatsi` command, and `tsatsi` for short, into `~/.local/bin` and runs `hiru-tsatsi set-up`, which gives Hiru Tsatsi the first free shortcut of SUPER + CTRL + U, SUPER + ALT + U and SUPER + SHIFT + U, and a notification at login asking whether to start your work apps. `hiru-tsatsi start` starts them straight away.

When [window-names](https://github.com/Libertas-le-Spes/window-names) is installed, every window Hiru Tsatsi gives to an app is also named after it in `~/.local/state/window-names/<window address>`, so title bars can say "Rider Main" rather than "jetbrains-rider". `hiru-tsatsi window-titles off` stops that, and `on` starts it even without window-names.

The app list is kept in `~/.config/hiru-tsatsi/apps.json`. `hiru-tsatsi add-workspace`, `remove-workspace`, `add-app` and `remove-app` change it from a terminal or a bar. There is no editing page in the browser: it was removed because any other account on the machine could use it to run commands as you (see `docs/security-review.md`, H1), and nothing that opens a port will come back without a way to refuse other accounts. Until it exists, the list is imported once from where Hiru Tsatsi kept it when it was called Workbench (`~/.config/workbench/apps.json`), or else from the Omarchy Omastart plugin.

Desktops so far: Hyprland.

Needs Python 3.11 or newer and nothing else.
