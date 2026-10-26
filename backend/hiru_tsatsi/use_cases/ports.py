from typing import Protocol

from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.shortcut import Keys
from hiru_tsatsi.work_apps.windows import Window


class DesktopNotSupported(Exception):
    def __init__(self, desktop: str):
        super().__init__(desktop)
        self.desktop = desktop


class SetUpFailed(Exception):
    pass


class ConfigLeftAlone(Exception):
    pass


class Launched(Protocol):
    def stopped(self) -> bool: ...


class Desktop(Protocol):
    def windows(self) -> list[Window]: ...

    def launch(self, command: str, workspace: int) -> Launched: ...

    def launch_in_terminal(self, command: str, workspace: int, window: str) -> None: ...

    def move(self, window: Window, workspace: int) -> None: ...


class AppListStore(Protocol):
    def load(self) -> AppList: ...

    def save(self, apps: AppList) -> None: ...


class WindowNames(Protocol):
    def record(self, window: Window, name: str) -> None: ...


class SettingsStore(Protocol):
    def window_titles(self) -> bool | None: ...

    def set_window_titles(self, on: bool) -> None: ...


class Announcer(Protocol):
    def announce(self, starting: list[str]) -> None: ...


class Notifier(Protocol):
    def notify(self, summary: str, body: str) -> None: ...

    def ask(self, summary: str, body: str, action: str) -> bool: ...


class DesktopSetUp(Protocol):
    def installed_keys(self) -> Keys | None: ...

    def taken_keys(self) -> set[Keys]: ...

    def install(self, keys: Keys | None, start_command: str, ask_command: str) -> None: ...
