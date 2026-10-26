from enum import Enum
from typing import Protocol

from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.shortcut import Keys
from hiru_tsatsi.work_apps.windows import Window


class Desktop(Protocol):
    def windows(self) -> list[Window]: ...

    def launch(self, command: str, workspace: int) -> None: ...

    def move(self, window: Window, workspace: int) -> None: ...


class Launch(Protocol):
    def wrapped(self, command: str) -> str: ...

    def stopped(self) -> bool: ...


class Launches(Protocol):
    def new(self) -> Launch: ...


class Terminal(Protocol):
    def command_for(self, command: str, window: str) -> str: ...


class Clock(Protocol):
    def now(self) -> float: ...

    def wait(self, seconds: float) -> None: ...


class OneStartAtATime(Protocol):
    def claimed(self) -> bool: ...


class Announcer(Protocol):
    def announce(self, starting: list[str]) -> None: ...


class AppListStore(Protocol):
    def load(self) -> AppList: ...

    def save(self, apps: AppList) -> None: ...


class WindowNames(Protocol):
    def record(self, window: Window, name: str) -> None: ...


class SettingsStore(Protocol):
    def window_titles(self) -> bool | None: ...

    def set_window_titles(self, on: bool) -> None: ...


class Answer(Enum):
    YES = "yes"
    NO = "no"
    NOT_SHOWN = "not shown"


class Notifier(Protocol):
    def notify(self, summary: str, body: str) -> None: ...

    def ask(self, summary: str, body: str, action: str) -> bool: ...

    def ask_within(self, summary: str, body: str, action: str, seconds: float) -> Answer: ...


class DesktopSetUp(Protocol):
    def installed_keys(self) -> Keys | None: ...

    def taken_keys(self) -> set[Keys]: ...

    def install(self, keys: Keys | None, command: str) -> None: ...


class CommandLinks(Protocol):
    def present(self, path: str) -> bool: ...

    def is_ours(self, path: str) -> bool: ...

    def link(self, path: str, target: str) -> None: ...

    def remove(self, path: str) -> None: ...
