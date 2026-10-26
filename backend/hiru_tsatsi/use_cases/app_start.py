from typing import Protocol

from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.windows import Window


class AppStart(Protocol):
    placement: Placement

    def next(self, now: float) -> "AppStart": ...

    def on_placed(self, window: Window, confirming: ConfirmingTerminals) -> None: ...
