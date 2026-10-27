from hiru_tsatsi.use_cases.app_start import AppStart, placements_of, still_waiting
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Clock, Desktop

POLL_SECONDS = 0.5
WATCH_SECONDS = 60.0


class WatchingStarts:
    def __init__(self, desktop: Desktop, clock: Clock, watch_seconds: float):
        self.desktop = desktop
        self.clock = clock
        self.watch_seconds = watch_seconds

    def until_placed(self, placing: PlacingWindows, starts: list[AppStart]) -> list[AppStart]:
        deadline = self.clock.now() + self.watch_seconds
        awaiting = starts
        while self._still_watching(awaiting, deadline):
            self.clock.wait(POLL_SECONDS)
            awaiting = self._moved_on(self._still_without_window(placing, awaiting))
        return awaiting

    def _still_watching(self, awaiting: list[AppStart], deadline: float) -> bool:
        if self.clock.now() >= deadline:
            return False
        return len(still_waiting(awaiting)) > 0

    def _still_without_window(self, placing: PlacingWindows, starts: list[AppStart]) -> list[AppStart]:
        unplaced = placing.place(placements_of(starts), self.desktop.windows())
        waiting = []
        for start in starts:
            if start.placement in unplaced:
                waiting.append(start)
        return waiting

    def _moved_on(self, starts: list[AppStart]) -> list[AppStart]:
        moved_on = []
        for start in starts:
            moved_on.append(start.next(self.clock.now()))
        return moved_on
