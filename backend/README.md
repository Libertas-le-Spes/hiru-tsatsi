# Hiru Tsatsi

This describes the project as it is now. Some of it may still change as the project grows; whoever makes part of it untrue updates it in the same change.

One key opens your work apps, each on the workspace you keep it on, on any Linux desktop.

Starting the day means opening the same apps and dragging each to its place. Doing it by hand is slow, and launchers that fire every command blindly open a second copy of whatever is already running, and leave windows wherever you happen to be. An app that hands the request to a copy already running (a web app inside an open browser, a second project in an open IDE, a game client in the tray) opens its window wherever you are, out of the launcher's reach.

So Hiru Tsatsi looks before it launches. Each app remembers its window: the start of its class, or of its title where several windows share a class. Apps already open are moved to their workspace instead of opened again; the rest all start at once, and each window is moved as it appears. Nobody has to know what a window class is: an app without one learns it from the first window that matches its command.

Only listing windows, moving them and launching differ between desktops, so each desktop is one class. On a desktop without one, Hiru Tsatsi starts nothing: apps opened without being put in their places would only leave the sorting to you.

Some apps live in a terminal and have no window of their own, such as `claude` or `nvim`. Started without a terminal they stop at once, unseen.

For a command that goes to a folder and runs a program (`cd ~/code && claude`), Hiru Tsatsi watches. The launch carries a random tag that the processes it starts inherit. When none of the owner's processes started since carries it, and no window has appeared ten seconds after launching, the app is reported as stopped without a window. Once the start is saved and reported, a notification asks whether to open it in a terminal, and closes itself after a minute. Nothing runs again without a click. Only one start runs at a time, held by a lock in `XDG_RUNTIME_DIR`, so a second press of the shortcut can't ask or launch the same app twice. A click opens it in a terminal (`xdg-terminal-exec`) with a window name of its own, and once the program is seen running there, the app is remembered as one that opens in a terminal. Anything but a click is saved as a no, and so is a trial that is never confirmed, so each app is asked about and tried once. Any other command is never watched or offered a terminal.

Such an app is also recognised by what runs inside a window: the program in the foreground of its terminal, and the folder it runs in, compared by where the command's folder really leads. A session opened by hand therefore counts as open whatever its title. A window whose program also draws other windows, or has more than one program inside, says nothing about what runs in it.

This needs a terminal that runs each window as its own process, as foot does on Omarchy. With one that runs all its windows from one process (Ghostty, or Kitty in single-instance mode), or starts its shells from a thread other than its first, nothing is read from inside, so a terminal app's one trial is never confirmed and sessions opened by hand are not recognised. A trial that is never confirmed, such as a typo or `btop`, whose folder Linux hides, waits its full minute before the second notification, the one that says which apps now open in a terminal.

Reading what runs inside windows sits in its own layer around the desktop, so each desktop class still only lists, moves and launches windows.

## Use

```sh
./install.sh
```

It links the `hiru-tsatsi` command, and `tsatsi` for short, into `~/.local/bin` and runs `hiru-tsatsi set-up`, which gives Hiru Tsatsi the first free shortcut of SUPER + CTRL + U, SUPER + ALT + U and SUPER + SHIFT + U, and a notification at login asking whether to start your work apps. On a desktop Hiru Tsatsi can't place windows on yet, the command is still installed and the shortcut and the question are skipped. `hiru-tsatsi start` starts them straight away.

When [window-names](https://github.com/Libertas-le-Spes/window-names) is installed, every window Hiru Tsatsi gives to an app is also named after it in `~/.local/state/window-names/<window address>`, so title bars can say "Rider Main" rather than "jetbrains-rider". `hiru-tsatsi window-titles off` stops that, and `on` starts it even without window-names.

The app list is kept in `~/.config/hiru-tsatsi/apps.json`. `hiru-tsatsi add-workspace`, `change-workspace`, `remove-workspace`, `add-app`, `change-app` and `remove-app` change it from a terminal or a bar. There is no editing page in the browser: it was removed because any other account on the machine could use it to run commands as you (see `docs/security-review.md`, H1), and nothing that opens a port will come back without a way to refuse other accounts. Until it exists, the list is imported once from where Hiru Tsatsi kept it when it was called Workbench (`~/.config/workbench/apps.json`), or else from the Omarchy Omastart plugin.

Desktops so far: Hyprland.

Needs Python 3.11 or newer and nothing else.
