from typing import Protocol

from workbench.work_apps.app_list import AppList
from workbench.work_apps.windows import Window


class DesktopNotSupported(Exception):
    def __init__(self, desktop: str):
        super().__init__(desktop)
        self.desktop = desktop


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
