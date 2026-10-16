from typing import Protocol

from workbench.work_apps.app_list import AppList
from workbench.work_apps.shortcut import Keys
from workbench.work_apps.windows import Window


class DesktopNotSupported(Exception):
    def __init__(self, desktop: str):
        super().__init__(desktop)
        self.desktop = desktop


class SetUpFailed(Exception):
    pass


class Desktop(Protocol):
    def windows(self) -> list[Window]: ...

    def launch(self, command: str, workspace: int) -> None: ...

    def move(self, window: Window, workspace: int) -> None: ...


class AppListStore(Protocol):
    def load(self) -> AppList: ...

    def save(self, apps: AppList) -> None: ...


class WindowNames(Protocol):
    def record(self, window: Window, name: str) -> None: ...


class Notifier(Protocol):
    def notify(self, summary: str, body: str) -> None: ...

    def ask(self, summary: str, body: str, action: str) -> bool: ...


class DesktopSetUp(Protocol):
    def installed_keys(self) -> Keys | None: ...

    def taken_keys(self) -> set[Keys]: ...

    def install(self, keys: Keys | None, start_command: str, ask_command: str) -> None: ...
