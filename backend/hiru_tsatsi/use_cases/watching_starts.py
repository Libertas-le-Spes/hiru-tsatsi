from typing import Callable

from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Desktop
from hiru_tsatsi.use_cases.start_shape import AppStart
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.windows import Window

POLL_SECONDS = 0.5


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

    def until_placed(self, placing: PlacingWindows, starts: list[AppStart]) -> list[Placement]:
        deadline = self.clock() + self.watch_seconds
        awaiting = starts
        while self._anything_to_wait_for(placing, awaiting) and self.clock() < deadline:
            self.wait(POLL_SECONDS)
            windows = self.desktop.windows()
            awaiting = self._still_without_window(placing, awaiting, windows)
            placing.confirm_terminals(windows)
            awaiting = self._moved_on(awaiting)
        return _placements(awaiting)

    @staticmethod
    def _anything_to_wait_for(placing: PlacingWindows, awaiting: list[AppStart]) -> bool:
        return len(awaiting) > 0 or len(placing.unconfirmed_terminals) > 0

    def _still_without_window(self, placing: PlacingWindows, starts: list[AppStart],
                              windows: list[Window]) -> list[AppStart]:
        unplaced = placing.place(_placements(starts), windows)
        waiting = []
        for start in starts:
            if start.placement in unplaced:
                waiting.append(start)
            else:
                start.on_placed(placing)
        return waiting

    def _moved_on(self, starts: list[AppStart]) -> list[AppStart]:
        moved_on = []
        for start in starts:
            moved_on.append(start.next(self.clock()))
        return moved_on
