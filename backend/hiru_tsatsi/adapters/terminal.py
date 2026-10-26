import shlex

KEEP_OPEN_AFTER_FAILURE = ('status=$?; [ "$status" -eq 0 ] || '
                           '{ printf "\\nStopped with exit code %s. Press Enter to close. " "$status"; read -r _; }')


def in_terminal(command: str, window: str) -> str:
    script = f"(\n{command}\n)\n{KEEP_OPEN_AFTER_FAILURE}"
    return f"xdg-terminal-exec --app-id={shlex.quote(window)} -- sh -c {shlex.quote(script)}"
