import shlex

KEEP_OPEN_AFTER_FAILURE = """status=$?
if [ "$status" -ne 0 ]; then
    printf '\\nStopped with exit code %s. Press Enter to close. ' "$status"
    read -r _
fi"""


def _script(command: str) -> str:
    in_its_own_shell = f"(\n{command}\n)"
    return f"{in_its_own_shell}\n{KEEP_OPEN_AFTER_FAILURE}"


class XdgTerminal:
    def command_for(self, command: str, window: str) -> str:
        app_id = shlex.quote(window)
        script = shlex.quote(_script(command))
        return f"xdg-terminal-exec --app-id={app_id} -- sh -c {script}"
