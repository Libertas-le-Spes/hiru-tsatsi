from dataclasses import dataclass

from hiru_tsatsi.use_cases.app_start import AppStart
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.windows import Window


@dataclass(frozen=True)
class OwnWindowStart:
    placement: Placement

    @classmethod
    def begin(cls, launcher: Launcher, placement: Placement, now: float) -> "OwnWindowStart":
        launcher.launch_plainly(placement)
        return cls(placement)

    def next(self, now: float) -> AppStart:
        return self

    def on_placed(self, window: Window, confirming: ConfirmingTerminals) -> None:
        return None
