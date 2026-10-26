from hiru_tsatsi.work_apps.shortcut import Keys


class FakeSetUp:
    def __init__(self, taken: set[Keys] | None = None, installed: Keys | None = None):
        if taken is None:
            taken = set()
        self.taken = taken
        self.installed = installed
        self.installs: list[tuple[Keys | None, str, str]] = []

    def installed_keys(self) -> Keys | None:
        return self.installed

    def taken_keys(self) -> set[Keys]:
        return self.taken

    def install(self, keys: Keys | None, start_command: str, ask_command: str) -> None:
        self.installs.append((keys, start_command, ask_command))
