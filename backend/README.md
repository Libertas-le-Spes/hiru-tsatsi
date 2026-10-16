# Workbench

One key opens your work apps, each on the workspace you keep it on, on any Linux desktop.

Starting the day means opening the same apps and dragging each to its place. Doing it by hand is slow, and launchers that fire every command blindly open a second copy of whatever is already running, and leave windows wherever you happen to be. An app that hands the request to a copy already running (a web app inside an open browser, a second project in an open IDE, a game client in the tray) opens its window wherever you are, out of the launcher's reach.

So Workbench looks before it launches. Each app remembers its window: the start of its class, or of its title where several windows share a class. Apps already open are moved to their workspace instead of opened again; the rest all start at once, and each window is moved as it appears. Nobody has to know what a window class is: an app without one learns it from the first window that matches its command.

Only listing windows, moving them and launching differ between desktops, so each desktop is one class and anything without one still gets its apps launched.

## Use

```sh
backend/bin/workbench start
```

The app list is kept in `~/.config/workbench/apps.json`. Until it exists, the list from the Omarchy Omastart plugin is used.

Desktops that can place windows: Hyprland. Everywhere else, apps are launched but not moved.

Needs Python 3.10 or newer and nothing else.
