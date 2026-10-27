from dataclasses import dataclass

from hiru_tsatsi.use_cases.app_start import AppStart
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising


@dataclass(frozen=True)
class TerminalStart:
    placement: Placement
    waits_for_window = True

    @staticmethod
    def fits(app: App, recognising: Recognising) -> bool:
        return recognising.is_terminal_app(app)

    @classmethod
    def begin(cls, launcher: Launcher, placement: Placement, now: float) -> "TerminalStart":
        launcher.launch_in_terminal(placement)
        return cls(placement)

    def next(self, now: float) -> AppStart:
        return self
