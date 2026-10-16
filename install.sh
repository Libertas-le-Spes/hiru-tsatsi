#!/bin/sh
set -eu

here=$(cd "$(dirname "$0")" && pwd)
bin_dir="$HOME/.local/bin"
command_path="$bin_dir/workbench"

say() {
    printf '%s\n' "$1"
}

fail() {
    printf 'workbench install: %s\n' "$1" >&2
    exit 1
}

require_python() {
    command -v python3 >/dev/null 2>&1 || fail "Python 3.10 or newer is needed; install python3 with your package manager"
    python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || fail "Python 3.10 or newer is needed; this machine has $(python3 --version)"
}

link_command() {
    mkdir -p "$bin_dir"
    ln -sfn "$here/backend/bin/workbench" "$command_path"
    say "command:  $command_path"
    case ":$PATH:" in
        *":$bin_dir:"*) ;;
        *) say "          $bin_dir is not on your PATH; add it to type 'workbench' anywhere" ;;
    esac
}

mention_missing_tools() {
    command -v notify-send >/dev/null 2>&1 || say "missing:  notify-send, so there is no question at login and no report after starting (it comes with libnotify)"
}

require_python
link_command
"$command_path" set-up
mention_missing_tools
