#!/bin/sh
set -eu

here=$(cd "$(dirname "$0")" && pwd)
bin_dir="$HOME/.local/bin"
command_path="$bin_dir/hiru-tsatsi"
short_path="$bin_dir/hiru"

say() {
    printf '%s\n' "$1"
}

fail() {
    printf 'hiru-tsatsi install: %s\n' "$1" >&2
    exit 1
}

require_python() {
    command -v python3 >/dev/null 2>&1 || fail "Python 3.11 or newer is needed; install python3 with your package manager"
    python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' || fail "Python 3.11 or newer is needed; this machine has $(python3 --version)"
}

refuse_to_replace_another_tool() {
    for path in "$command_path" "$short_path"; do
        if [ -e "$path" ] || [ -L "$path" ]; then
            case "$(readlink "$path" || true)" in
                */backend/bin/hiru-tsatsi) ;;
                *) fail "$path is already there and is not Hiru Tsatsi; move it away and run install.sh again" ;;
            esac
        fi
    done
}

link_command() {
    mkdir -p "$bin_dir"
    ln -sfn "$here/backend/bin/hiru-tsatsi" "$command_path"
    ln -sfn "$here/backend/bin/hiru-tsatsi" "$short_path"
    say "command:  $command_path, and $short_path for short"
    case ":$PATH:" in
        *":$bin_dir:"*) ;;
        *) say "          $bin_dir is not on your PATH; add it to type 'hiru' anywhere" ;;
    esac
}

mention_missing_tools() {
    command -v notify-send >/dev/null 2>&1 || say "missing:  notify-send, so there is no question at login and no report after starting (it comes with libnotify)"
}

require_python
refuse_to_replace_another_tool
link_command
"$command_path" set-up
mention_missing_tools
