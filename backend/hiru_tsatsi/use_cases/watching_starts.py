from typing import Callable

from hiru_tsatsi.use_cases.app_start import AppStart
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Desktop
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.windows import Window

POLL_SECONDS = 0.5
WATCH_SECONDS = 60.0


def _waiting_for_a_window(starts: list[AppStart]) -> bool:
    for start in starts:
        if start.waits_for_window:
            return True
    return False


def _placements(starts: list[AppStart]) -> list[Placement]:
    placements = []
    for start in starts:
        placements.append(start.placement)
    return placements


class WatchingStarts:
    def __init__(self, desktop: Desktop, clock: Callable[[], float], wait: Callable[[float], None],
                 watch_seconds: float):
        self.desktop = desktop
        self.clock = clock
        self.wait = wait
        self.watch_seconds = watch_seconds

    def until_placed(self, placing: PlacingWindows, confirming: ConfirmingTerminals,
                     starts: list[AppStart]) -> list[AppStart]:
        deadline = self.clock() + self.watch_seconds
        awaiting = starts
        while (_waiting_for_a_window(awaiting) or confirming.waiting) and self.clock() < deadline:
            self.wait(POLL_SECONDS)
            windows = self.desktop.windows()
            awaiting = self._still_without_window(placing, confirming, awaiting, windows)
            self._remember_confirmed_terminals(placing, confirming, windows)
            awaiting = self._moved_on(awaiting)
        return awaiting

    def now(self) -> float:
        return self.clock()

    @staticmethod
    def _still_without_window(placing: PlacingWindows, confirming: ConfirmingTerminals, starts: list[AppStart],
                              windows: list[Window]) -> list[AppStart]:
        unplaced = placing.place(_placements(starts), windows)
        waiting = []
        for start in starts:
            if start.placement in unplaced:
                waiting.append(start)
            else:
                start.on_placed(placing.window_given_to(start.placement), confirming)
        return waiting

    @staticmethod
    def _remember_confirmed_terminals(placing: PlacingWindows, confirming: ConfirmingTerminals,
                                      windows: list[Window]) -> None:
        for placement in confirming.newly_confirmed(windows):
            placing.remember_terminal(placement)

    def _moved_on(self, starts: list[AppStart]) -> list[AppStart]:
        moved_on = []
        for start in starts:
            moved_on.append(start.next(self.clock()))
        return moved_on
