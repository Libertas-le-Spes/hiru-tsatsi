from dataclasses import dataclass

from hiru_tsatsi.use_cases.app_start import AppStart
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.ports import Launch
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.windows import Window

GIVE_UP_AFTER_SECONDS = 10.0


@dataclass(frozen=True)
class WatchedStart:
    placement: Placement
    launch: Launch
    since: float
    waits_for_window = True

    @staticmethod
    def fits(app: App, recognising: Recognising) -> bool:
        return recognising.recognised_by_what_runs(app) and not app.terminal_ruled_out

    @classmethod
    def begin(cls, launcher: Launcher, placement: Placement, now: float) -> "WatchedStart":
        return cls(placement, launcher.launch_watched(placement), now)

    def next(self, now: float) -> AppStart:
        if not self.stopped_without_window(now):
            return self
        return StoppedWithoutWindow(self.placement)

    def stopped_without_window(self, now: float) -> bool:
        waited_long_enough = now - self.since >= GIVE_UP_AFTER_SECONDS
        return waited_long_enough and self.launch.stopped()

    def on_placed(self, window: Window, confirming: ConfirmingTerminals) -> None:
        return None


@dataclass(frozen=True)
class StoppedWithoutWindow:
    placement: Placement
    waits_for_window = False

    def next(self, now: float) -> AppStart:
        return self

    def on_placed(self, window: Window, confirming: ConfirmingTerminals) -> None:
        return None
