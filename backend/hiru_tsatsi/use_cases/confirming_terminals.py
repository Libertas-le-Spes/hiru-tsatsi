from dataclasses import dataclass

from hiru_tsatsi.use_cases.ports import Clock, Desktop
from hiru_tsatsi.use_cases.watching_starts import POLL_SECONDS
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.windows import Window


@dataclass(frozen=True)
class Trial:
    placement: Placement
    window: Window


class ConfirmingTerminals:
    def __init__(self, desktop: Desktop, clock: Clock, recognising: Recognising, confirm_seconds: float):
        self.desktop = desktop
        self.clock = clock
        self.recognising = recognising
        self.confirm_seconds = confirm_seconds

    def confirmed_among(self, trials: list[Trial]) -> list[Placement]:
        deadline = self.clock.now() + self.confirm_seconds
        confirmed = []
        waiting = self._newly_confirmed(trials, confirmed)
        while waiting and self.clock.now() < deadline:
            self.clock.wait(POLL_SECONDS)
            waiting = self._newly_confirmed(waiting, confirmed)
        return confirmed

    def _newly_confirmed(self, trials: list[Trial], confirmed: list[Placement]) -> list[Trial]:
        windows = self.desktop.windows()
        waiting = []
        for trial in trials:
            if self._runs_in_window_at(trial.placement, trial.window.address, windows):
                confirmed.append(trial.placement)
            else:
                waiting.append(trial)
        return waiting

    def _runs_in_window_at(self, placement: Placement, address: str, windows: list[Window]) -> bool:
        for window in windows:
            if window.address == address:
                return self.recognising.runs_inside(placement.app, window)
        return False
