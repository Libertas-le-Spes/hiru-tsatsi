from dataclasses import dataclass

from hiru_tsatsi.use_cases.app_start import AppStart
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.terminal_window import as_terminal_app
from hiru_tsatsi.work_apps.windows import Window


@dataclass(frozen=True)
class TerminalStart:
    placement: Placement
    waits_for_window = True

    @staticmethod
    def fits(app: App, recognising: Recognising) -> bool:
        return app.opens_in_terminal and recognising.recognised_by_what_runs(app)

    @classmethod
    def begin(cls, launcher: Launcher, placement: Placement, now: float) -> "TerminalStart":
        launcher.launch_in_terminal(placement)
        return cls(placement)

    def next(self, now: float) -> AppStart:
        return self

    def on_placed(self, window: Window, confirming: ConfirmingTerminals) -> None:
        return None


@dataclass(frozen=True)
class TrialTerminalStart:
    placement: Placement
    waits_for_window = True

    @classmethod
    def begin(cls, launcher: Launcher, placement: Placement) -> "TrialTerminalStart":
        trial = Placement(placement.workspace, placement.index, as_terminal_app(placement.app))
        launcher.launch_in_terminal(trial)
        return cls(trial)

    def next(self, now: float) -> AppStart:
        return self

    def on_placed(self, window: Window, confirming: ConfirmingTerminals) -> None:
        confirming.try_out(self.placement, window)
