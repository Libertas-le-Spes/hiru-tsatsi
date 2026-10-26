from typing import Protocol

from hiru_tsatsi.work_apps.placement import Placement


class Remembering(Protocol):
    def remember_terminal(self, placement: Placement) -> None: ...


class AppStart(Protocol):
    placement: Placement

    def next(self, now: float) -> "AppStart": ...

    def on_placed(self, remembering: Remembering) -> None: ...
