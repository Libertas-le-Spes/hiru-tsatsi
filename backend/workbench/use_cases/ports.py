from typing import Protocol

from workbench.work_apps.app_list import AppList
from workbench.work_apps.windows import Window


class Desktop(Protocol):
    sees_windows: bool

    def windows(self) -> list[Window]: ...

    def launch(self, command: str, workspace: int) -> None: ...

    def move(self, window: Window, workspace: int) -> None: ...


class AppListStore(Protocol):
    def load(self) -> AppList: ...

    def save(self, apps: AppList) -> None: ...


class Notifier(Protocol):
    def notify(self, summary: str, body: str) -> None: ...
