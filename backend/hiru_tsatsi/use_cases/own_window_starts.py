from dataclasses import dataclass

from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.start_shape import AppStart, Remembering
from hiru_tsatsi.work_apps.placement import Placement


@dataclass(frozen=True)
class OwnWindowStart:
    placement: Placement

    @classmethod
    def begin(cls, launcher: Launcher, placement: Placement, now: float) -> "OwnWindowStart":
        launcher.plainly(placement)
        return cls(placement)

    def next(self, now: float) -> AppStart:
        return self

    def on_placed(self, remembering: Remembering) -> None:
        return None
