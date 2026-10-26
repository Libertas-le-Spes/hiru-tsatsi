from typing import Callable

from hiru_tsatsi.use_cases.app_starts import AppStart
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Desktop
from hiru_tsatsi.use_cases.terminal_starts import TrialTerminalStart
from hiru_tsatsi.work_apps.placement import Placement

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
        while awaiting and self.clock() < deadline:
            self.wait(POLL_SECONDS)
            awaiting = self._terminals_where_needed(awaiting)
            awaiting = self._still_without_window(placing, awaiting)
        return _placements(awaiting)

    def _terminals_where_needed(self, starts: list[AppStart]) -> list[AppStart]:
        checked = []
        for start in starts:
            if start.needs_terminal(self.clock()):
                start = TrialTerminalStart.begin(self.desktop, start.placement)
            checked.append(start)
        return checked

    def _still_without_window(self, placing: PlacingWindows, starts: list[AppStart]) -> list[AppStart]:
        unplaced = placing.place(_placements(starts), self.desktop.windows())
        waiting = []
        for start in starts:
            if start.placement in unplaced:
                waiting.append(start)
            else:
                start.on_placed(placing)
        return waiting
