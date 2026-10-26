# Security review

This review describes the repository at commit `8372a7c` (main, 2026-10-22). Some of what it
proposes is planned, not done, and it will change as the project grows. Whoever fixes a finding,
or makes part of this document untrue, updates it in the same pull request.

Hiru Tsatsi starts a person's work apps, each on its own workspace. It has three faces: the bar
panel in the Omarchy shell (`Panel.qml`), the `hiru-tsatsi` / `hiru` command (`backend/`), and a
small editing page that `hiru-tsatsi edit` serves to the browser. Every app in the list is a real
shell command that Hiru Tsatsi runs, on purpose. So the question this review asks throughout is:
**who, other than the owner, can put a command into that list or make Hiru Tsatsi run one?**

## Verdict

One finding is **High**: while the editing page is open, any other account on the same machine
can add a command to the owner's list and start it, running it as the owner. It is the same
shape as the issue just fixed in a sibling project, and as CVE-2026-33898 in Incus: a page on
127.0.0.1 protects its API with a token, then hands the token to anyone who asks for the page.

The rest of the code is careful. No Python code goes through a shell except the one place that
is meant to (launching an app), the bar builds argument lists rather than shell strings, files
are written owner-only and atomically, and the editing page renders everything as text. The other
findings are two Medium issues around the editing page and the launcher, and a handful of Low and
Info items.

On a machine with one person and no services running under other accounts, the High finding has
nobody to exploit it. On a shared machine, or one running containers or services under their own
accounts, it is a real path to the owner's session.

## Status

Every finding below is dealt with on the branch `security-fixes-hiru`. The owner chose option A
for H1: the editing page is gone, so Hiru Tsatsi no longer listens for connections at all, and a
test fails if any module imports a web server, a socket or a browser opener. That also removes M2
and L2, which were about the same page. Each other finding was fixed as its section proposes and
sealed by the test it names. The line numbers below describe commit `8372a7c`, before the fixes. The
short command the findings call `hiru` is now `tsatsi`.

"Checked and found sound" and the step plan describe commit `8372a7c` as it was reviewed. Since
then the page, its server and its rendering are gone, so the items about them no longer apply;
steps 1, 2, 4 and 5 of the plan became the single step of removing the page. Every write now
refuses a folder that belongs to another account or that other accounts can write to. A write
replaces a link rather than following it, except for the two Hyprland config files, where a
linked dotfile is expected; there the folder holding the link must pass the same check. A file
that exists but can't be read or parsed is refused rather than treated as empty, so a typo in
`apps.json` never wipes the list. Window-name files are written only for Hyprland addresses (`0x`
followed by hex digits). The panel's window-choice buttons show web-page titles through Omarchy's
own `Button`, which sets `Text.PlainText` (`/usr/share/omarchy/shell/Ui/Button.qml`); that safety
lives outside this repository.

## Findings

| Id | Severity | Title | Location | Status |
|---|---|---|---|---|
| H1 | High | The editing page gives its key to anyone who asks, so any local account can add and start commands as the owner | `backend/hiru_tsatsi/entrypoints/web/server.py:65-67, 87-94`; `backend/page/index.html:6` | Fixed: page removed (option A) |
| M1 | Medium | `hiru` runs Python files from whichever folder it is started in | `backend/bin/hiru-tsatsi:2` | Fixed: `-P`, Python 3.11 |
| M2 | Medium | `hiru edit` sends the browser to whatever program already holds port 47640 | `backend/hiru_tsatsi/entrypoints/web/server.py:15, 55-59` | Fixed: page removed |
| L1 | Low | The bar panel renders window titles as rich text, so any web page's title can make the bar fetch a URL | `Panel.qml:304-306` (and every other bare `Text`) | Fixed: every `Text` plain |
| L2 | Low | The editing page can be framed by another site (no framing or content-security headers) | `backend/hiru_tsatsi/entrypoints/web/server.py:137-143` | Fixed: page removed |
| L3 | Low | `set-up` rewrites the main Hyprland config in place, so a crash mid-write can empty it | `backend/hiru_tsatsi/adapters/desktops/hyprland_set_up.py:41, 54-58` | Fixed: one atomic writer |
| I1 | Info | The command path written into the Hyprland config is not shell-quoted, and newlines are not escaped for Lua | `backend/hiru_tsatsi/adapters/desktops/hyprland_set_up.py:49-52`; `hyprland.py:15-16` | Fixed |
| I2 | Info | `install.sh` silently replaces any existing `hiru` in `~/.local/bin` | `install.sh:25-26` | Fixed |
| I3 | Info | App commands are visible to every account in the process list while they launch | `backend/hiru_tsatsi/adapters/desktops/hyprland.py:40` | README says so |

All examples and outputs below use made-up apps, names and folders.

---

### H1 — The editing page gives its key to anyone who asks

**What it is.** `hiru-tsatsi edit` starts a small web server on 127.0.0.1, port 47640, and opens
the editing page in the browser. Through that server the page can add, change and remove apps,
and press **Start work apps**. To stop strangers from calling it, the server makes a random token
and refuses any API call that does not carry it.

**The point.** The server writes that token into the page itself (`<meta name="token">`) and
serves the page to any request whose `Host` header names 127.0.0.1. On Linux every account on the
machine can connect to 127.0.0.1, and anyone writing their own request can set `Host` to anything.
So the token stops nobody who can open a connection: they ask for the page, read the token, and
then use the whole API.

Run against a server on a random port with a fake desktop and a throwaway list:

| Step | Request | Result |
|---|---|---|
| 1 | API call without the token | `403 forbidden` |
| 2 | Ask for the page `/`, without the token | `200`, page carries a 43-character token equal to the server's |
| 3 | Add a workspace, with that token | `200` |
| 4 | Add an app with command `example-command --flag`, with that token | `200`; the saved list now holds `example-command --flag` |
| 5 | Start work apps, with that token | `200`; the desktop is asked to launch `('example-command --flag', 9)` |

**What happens if it is left alone.** While the owner has the editing page open (and for two
minutes after they close it; the open tab keeps the server alive indefinitely), any other account
on the machine can add a command and start it at once. The command runs as the owner, inside
their desktop session, with their files, keys and browser profile. It also stays in the list, so
it runs again every time the owner starts their work apps. "Another account" includes a person
sharing the machine, and also a service or container that shares the host's network but runs
under its own account (a database, a web server or a build agent that has itself been
compromised). The owner sees nothing unless they read the list closely.

Whether a web page in the owner's own browser can do the same was checked by reading the code,
not demonstrated in a real browser. It cannot read the page across origins (no CORS headers are
sent), cannot add the custom token header without a CORS preflight the server never answers, and
DNS-rebinding is stopped by the `Host` check. The cross-account path was demonstrated on one
account only; no second account was available to show the refusal is missing across accounts,
but nothing in the server looks at who is connecting, and loopback TCP has no per-account access
control.

**Fix options, safest first.**

| Option | What it is | What it still fails to stop |
|---|---|---|
| A. Remove the editing page | Edit only through the bar panel and the CLI, which never open a port | Nothing new; but it removes the only graphical editor off Omarchy |
| B. Refuse other accounts at the door | For each connection, look up the owner of the connecting socket in `/proc/net/tcp` and refuse unless it is the owner's account; refuse when it can't be found | Processes running as the owner (they can already edit `apps.json` directly); a page in the owner's own browser (the existing `Host` and header checks cover that) |
| C. Stop handing out the token | Never put the token in any response. Open the browser on an owner-only file in `$XDG_RUNTIME_DIR` that forwards to `http://127.0.0.1:<port>/#<token>`; the page reads the token from the fragment, removes it from the address bar and sends it as a header | A second account that wins a race to read the forwarding file (it can't: the folder is `0700`); browser history may keep the first address (owner only); sandboxed browsers that can't read the file fail closed |
| D. Random port each run | Bind port 0 instead of 47640 | On its own, nothing: a port scan finds it in milliseconds |
| E. Token in a cookie | Exchange the token for an `HttpOnly` cookie | Cookies are not isolated by port (RFC 6265 §8.5), so any other server on 127.0.0.1 the browser visits receives it. **Rejected.** |
| F. Token in the URL passed to the browser | `webbrowser.open("http://127.0.0.1:port/?token=...")` | The URL becomes an argument of `xdg-open` and the browser, and `/proc/<pid>/cmdline` is world-readable (`-r--r--r--` here). **Rejected.** |

**Recommendation: B, then C, then D, layered**, plus the headers from L2. B alone closes H1 for
every other account and fails closed: a connection whose owner can't be proven is refused. C
removes the leak itself, so the server stays safe even where B can't run (another kernel, a
future port to a non-Linux desktop). D, combined with the M2 fix, means a page left open by an
earlier squatter never shares an origin with the real one. Together they leave only the owner's
own processes, which can already write the list file, so the page adds no new way in. A is the
only option with strictly fewer gaps, because it removes the listener. Take A instead if the
page is rarely used outside Omarchy, since the bar panel and CLI already cover editing.

A prototype of B's lookup, run here:

```
connecting socket owned by uid 1000 | this process uid 1000
unknown connection -> None (refuse: fail closed)
```

**Until B ships:** on a shared machine, edit through the bar panel or the CLI and don't run
`hiru-tsatsi edit`. Neither of those opens a port.

**How to seal it.**

- Make the wrong thing impossible: `PageServer` takes a `Peers` object (one small interface,
  `owner_of(client, server) -> int | None`) as a required constructor argument with no default.
  The Linux implementation reads `/proc/net/tcp`; tests pass a fake. A server that skips the check
  can't be built.
- Test: for every route, including `/` and the static files, a connection whose owner is another
  account, or unknown, gets `403`.
- Test: no response from the server, for any route, with or without a valid token, contains the
  token (`page.token not in body`).
- Architecture test: `backend/page/` contains no `{{token}}` placeholder, and `server.py` never
  formats the token into a body.

---

### M1 — `hiru` runs Python files from whichever folder it is started in

**What it is.** `hiru` and `hiru-tsatsi` are a two-line shell script that runs
`python3 -m hiru_tsatsi`. Python's `-m` puts the current folder first on the import path, ahead
of the standard library.

**The point.** Starting `hiru` from a folder that contains a file named like a standard module
(`json.py`, `argparse.py`, `pathlib.py`) runs that file instead, as the owner. Run against a
made-up folder holding a `json.py` that leaves a marker:

| How it is launched | Planted file ran? |
|---|---|
| Current launcher (`python3 -m hiru_tsatsi`) | **yes** (`exit=1`, marker written) |
| `python3 -P -m hiru_tsatsi` | no |
| `python3 -I -c '…insert path…; run_module(…)'` | no |

**What happens if it is left alone.** Someone who clones a repository, unpacks an archive or opens
a shared folder and types `hiru start` there runs whatever Python the author of that folder left.
The bar and the keyboard shortcut start Hiru Tsatsi from the home folder, so they are not affected.

**Fix options.**

| Option | What it still fails to stop |
|---|---|
| `python3 -P -m hiru_tsatsi`, and raise the minimum to Python 3.11 | Same-account environment variables and user site-packages (only the owner can write those). Python 3.10 refuses the unknown `-P` option, so it fails closed. |
| `python3 -I` with the package path inserted by a one-line `-c` | The same, plus it ignores `PYTHON*` variables; but harder to read, and `-I` for `-c` is documented only by implication |
| `cd` to the package folder before running | Changes the folder the user's commands see; breaks relative paths |

**Recommendation:** `-P` with Python 3.11 as the minimum (`install.sh` checks for it). It closes
everything a different party can reach, reads plainly, and refuses to run rather than run unsafely
on 3.10. Arch ships 3.14.

**How to seal it.** A test runs the real launcher from a temporary folder containing a planted
`json.py` that writes a marker, and asserts the marker is absent.

---

### M2 — `hiru edit` sends the browser to whatever already holds port 47640

**What it is.** When `edit` can't bind its fixed port, it assumes an earlier copy of itself is
already serving and opens the browser on that port anyway.

**The point.** Any program can hold that port, including one run by another account. Run with a
stand-in holding a random port:

```
another program already holds the port -> already open | browser sent to: ['http://127.0.0.1:48379/']
```

**What happens if it is left alone.** Another account that holds 47640 gets the owner's browser
pointed at its own page, which can look exactly like the editing page and ask for anything. Worse,
if that page stays open in a tab and the squatter later lets the port go, the owner's next real
`hiru edit` serves from the *same origin* as the squatter's tab, which can then use the real page's
API. Fixing H1 with option C alone would not stop that chain; B and the random port do.

**Fix.** Bind port 0 (a fresh random port each run) and open the browser only on a port this
process bound. Fail closed: if binding fails, say so and open nothing. What it fails to stop: two
`edit` runs give two tabs, which is harmless.

**How to seal it.** A test holds a port, calls `serve` on it, and asserts the browser opener was
never called.

---

### L1 — The bar panel renders window titles as rich text

**What it is.** Under each app the panel shows where its window is, for example
"✓ Example Site, open on workspace 1". The title comes from the window itself, and a browser
window's title is whatever the page in its active tab sets.

**The point.** The panel draws that line with a plain Qt `Text`, whose default format is
`AutoText`: if the text looks like HTML, Qt renders it as rich text, and rich text can load images
over the network. Rendered on Qt 6's offscreen platform with a made-up title containing an image
tag pointing at a local listener:

| `textFormat` | Listener log |
|---|---|
| default (`AutoText`), as in `Panel.qml` today | `beacon received: /seen.png` |
| `Text.PlainText` | nothing (0 lines) |

**What happens if it is left alone.** Any web site the owner keeps open in an app's window can set
its title so that opening the bar panel fetches a URL of its choosing, telling the site when the
panel is opened, and can restyle or spoof the status line. It can't run code. The panel's buttons
already use the shell's `Button`, which is plain text; the seven bare `Text` items in `Panel.qml`
are not.

**Fix options.** (a) Set `textFormat: Text.PlainText` on the status line only, which fails to stop
the next `Text` someone adds. (b) Set it on every `Text` in the plugin, sealed by a test.
(c) Escape titles in the backend, which is the wrong layer and fails for any other reader.
**Recommendation: (b).** Qt's own documentation says to set `PlainText` for untrusted content.

**How to seal it.** A test reads every `.qml` file in the repository and fails if any `Text {`
block lacks `textFormat: Text.PlainText`.

---

### L2 — The editing page can be framed by another site

**What it is.** The server sends no `Content-Security-Policy`, `X-Frame-Options` or
`Referrer-Policy` headers.

**What happens if it is left alone.** While the page is open, a web site could load it in a hidden
frame and trick the owner into clicking **Start work apps** or a remove button (clickjacking).
Typing a command through a frame is much harder. Newer Chrome versions ask before public sites
reach the local network, which makes this harder still. Not demonstrated in a browser.

**Fix.** Send `Content-Security-Policy: default-src 'self'; frame-ancestors 'none'; base-uri 'none';
form-action 'none'`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` and
`Referrer-Policy: no-referrer` on every response. What it fails to stop: nothing in this class;
browsers too old to know `frame-ancestors` fall back to `X-Frame-Options`.

**How to seal it.** A test asserts every response, including 403 and 404, carries these headers.
Put them in the one method that sends responses, so no route can skip them.

---

### L3 — `set-up` rewrites the main Hyprland config in place

**What it is.** `set-up` adds one `dofile(...)` line to the owner's main Hyprland config and writes
its own small config file. Both are written with `write_text`, which empties the file and then
writes it. The inode stayed the same in a run against a made-up config, so the file really is
rewritten in place.

**What happens if it is left alone.** If the machine loses power or the process is killed between
those two moments, the owner's main desktop config is left empty or cut short, and the next login
comes up without their keybindings. It is not exploitable by anyone else, but it lands on the
owner's whole desktop.

**Fix.** Write to a temporary file in the same folder, copy the original's mode, flush, and
`os.replace` it over the resolved target, so a symlinked dotfile keeps its link. Before replacing,
check the file hasn't changed since it was read, and refuse if it has, so an edit the owner made in
the meantime isn't lost. What it fails to stop: an editor holding the file open with unsaved
changes, which no file-based approach can see.

**How to seal it.** Move the write into one atomic writer used by every storage class (the list
and settings files already do it this way). Tests: a writer that fails half-way leaves the
original intact; a symlinked main config is still a symlink afterwards.

---

### I1 — Quoting in the Hyprland config

The keybinding and login lines hand `~/.local/bin/hiru-tsatsi start` to a shell (`exec_cmd` runs
`sh -c`) without shell quoting, so a home folder containing a space or a shell character breaks the
binding. Only the owner or an administrator controls that folder name. Separately, `lua_string`
escapes quotes and backslashes but not newlines. Tested with Lua 5.4:

| Input | Result |
|---|---|
| `say "hi"`, `ends with \`, `a\" .. os.exit(7) .. "`, `]] .. os.exit(7) --[[`, a NUL, a tab | parsed back with the same length; no breakout |
| text with `\n` or `\r` | `unfinished string`: Lua refuses it (fails closed) |

**Fix.** Pass the path through `shlex.quote` before `lua_string`, and have `lua_string` escape
every control character as `\ddd`. **Seal:** a test with a made-up path containing a space and a
quote, and a table test of control characters.

### I2 — `install.sh` replaces any existing `hiru`

`ln -sfn` overwrites whatever is at `~/.local/bin/hiru`, which is a short and likely name. **Fix:**
replace it only if it is missing or already links into this repository; otherwise stop with a
message. **Seal:** a shell test in a temporary `HOME`.

### I3 — Commands are visible in the process list

Each launch passes the app's command to `hyprctl` and then `sh -c` as arguments, which every
account can read. That is unavoidable for a command run through a shell. **Fix:** say in the README
that the **Command** field is not a place for passwords or tokens; put those in a script that reads
them from a secret store.

---

## Checked and found sound

- **No hidden shell.** No `shell=True`, `os.system`, `os.popen` or `eval` in the backend. Every
  subprocess is an argument list. The bar's `Process` items are argument lists too, and Quickshell
  documents that `Process` "does not run command in a shell".
- **Launching is the only shell, by design.** An app's **Command** goes to Hyprland's `exec_cmd`,
  which runs it with `sh -c`; that is the feature. Lua quoting holds (I1 table). The trust boundary
  is who can write the list, and only the owner can, apart from H1.
- **Window addresses.** Moving a window uses the address Hyprland reported, Lua-quoted. Choosing a
  window from the page or CLI is checked against the currently open windows before it is saved.
  Window-name files are written only for addresses matching `[\w.-]+`, so a crafted address can't
  escape the folder.
- **Saved state.** `apps.json` and `settings.json` are written through `mkstemp` and `os.replace`
  in the same folder, owner-only (`-rw-------` in a test run), and replacing a symlink replaces the
  link rather than writing through it. Nothing is written under `/tmp`.
- **The editing page's own rendering (page since removed).** `page.js` builds every element with `textContent`; no
  `innerHTML`. A hostile window title shows as text on the page.
- **Browser attacks on the server (server since removed).** It binds 127.0.0.1 only; the `Host` check stops DNS
  rebinding; the token is compared in constant time; cross-site pages can't add the custom header
  without a CORS preflight that is never answered. Reasoned from code; not demonstrated in a browser.
- **Bar IPC.** The panel's IPC target exposes only open, close, show, hide and toggle.
- **Desktop entries.** The repository ships no `.desktop` files, so `Exec` field-code quoting does
  not apply.
- **Supply chain.** No third-party dependencies (Python standard library only), no
  `curl | sh`, and no GitHub Actions workflows to review.
- **Tests.** The existing 80 tests pass with every external command stubbed, and none of them
  tried to open a browser or notification.

## Step plan

Each step is small, ships on its own, and leaves the project safer than before. Order is by
safety, not ease.

1. **Refuse other accounts at the door (H1, option B).** Add a `Peers` interface and its
   `/proc/net/tcp` implementation in its own file under `adapters/`; make it a required argument of
   `PageServer`; refuse unknown owners. Tests from H1's seal. This alone closes H1.
2. **Random port, fail closed (M2, H1 option D).** Bind port 0; open the browser only on a port
   this process bound; drop the "already open" path. Test from M2's seal.
3. **Safe launcher (M1).** `python3 -P -m`, Python 3.11 minimum in `install.sh` and both READMEs.
   Planted-module test.
4. **Stop handing out the token (H1, option C).** Forwarding file in `$XDG_RUNTIME_DIR`, token in
   the fragment, never in a response. The file writer is its own class; the page reads and clears
   the fragment. Tests from H1's seal.
5. **Response headers (L2).** In the single send method. Header test.
6. **Plain text in the bar (L1).** `textFormat: Text.PlainText` on every `Text`; QML scan test.
7. **Atomic config writes (L3).** One atomic writer shared by all storage; failure and symlink
   tests.
8. **Quoting and install tidy-ups (I1, I2, I3).** Shell-quote the path, escape control characters,
   protect an existing `hiru`, and a README line on secrets.

If the editing page turns out to be rarely used, replace steps 1, 2, 4 and 5 with one step that
removes it (option A).

## Sources

- OWASP OS Command Injection Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- OWASP Input Validation Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
- OWASP File Upload Cheat Sheet (path handling) — https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- OWASP Clickjacking Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
- CWE-78 OS command injection — https://cwe.mitre.org/data/definitions/78.html
- CWE-88 argument injection — https://cwe.mitre.org/data/definitions/88.html
- CWE-22 path traversal — https://cwe.mitre.org/data/definitions/22.html
- CWE-59 link following — https://cwe.mitre.org/data/definitions/59.html
- CWE-367 TOCTOU race — https://cwe.mitre.org/data/definitions/367.html
- CWE-427 uncontrolled search path element (M1) — https://cwe.mitre.org/data/definitions/427.html
- CWE-668 exposure of resource to wrong sphere (H1) — https://cwe.mitre.org/data/definitions/668.html
- CWE-1021 improper restriction of rendered UI layers (L2) — https://cwe.mitre.org/data/definitions/1021.html
- CVE-2026-33898, Incus web UI on localhost reachable by other local users — https://nvd.nist.gov/vuln/detail/CVE-2026-33898
- Python 3.10 command line, `-m` and `-I` and `sys.path` — https://docs.python.org/3.10/using/cmdline.html
- Python security considerations, `-P` / `PYTHONSAFEPATH` — https://docs.python.org/3/library/security_warnings.html
- CPython change adding `-P` (gh-57684) — https://github.com/python/cpython/pull/92361
- Qt 6 `Text` QML type, `textFormat` and untrusted content — https://doc.qt.io/qt-6/qml-qtquick-text.html
- Qt development list, proposal to disable AutoText — https://lists.qt-project.org/pipermail/development/2026-July/047374.html
- Quickshell `Process` (argument list, no shell) — https://quickshell.org/docs/types/Quickshell.Io/Process/
- Hyprland dispatchers, `exec_cmd` runs `sh -c` — https://wiki.hypr.land/configuring/core/dispatchers/
- Waybar escaping window titles injected as markup — https://git.nixnet.services/blankie/Waybar/commit/157ea445102b0bc2db02733095a4350c7b2089d1
- Waybar custom module `escape` option — https://man.archlinux.org/man/waybar.5
- RFC 6265 §8.5, cookies are not isolated by port — https://datatracker.ietf.org/doc/html/rfc6265#section-8.5
- Chrome Local Network Access — https://developer.chrome.com/blog/local-network-access
- freedesktop Desktop Entry spec, `Exec` key (checked, not applicable) — https://specifications.freedesktop.org/desktop-entry/latest/exec-variables.html
