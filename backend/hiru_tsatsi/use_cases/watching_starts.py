from hiru_tsatsi.use_cases.app_start import AppStart, placements_of, still_waiting
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Clock, Desktop
from hiru_tsatsi.work_apps.windows import Window

POLL_SECONDS = 0.5
WATCH_SECONDS = 60.0


class WatchingStarts:
    def __init__(self, desktop: Desktop, clock: Clock, watch_seconds: float):
        self.desktop = desktop
        self.clock = clock
        self.watch_seconds = watch_seconds

    def until_placed(self, placing: PlacingWindows, confirming: ConfirmingTerminals,
                     starts: list[AppStart]) -> list[AppStart]:
        deadline = self.clock.now() + self.watch_seconds
        awaiting = starts
        while self._still_watching(awaiting, confirming, deadline):
            self.clock.wait(POLL_SECONDS)
            windows = self.desktop.windows()
            awaiting = self._still_without_window(placing, confirming, awaiting, windows)
            self._remember_confirmed_terminals(placing, confirming, windows)
            awaiting = self._moved_on(awaiting)
        return awaiting

    def _still_watching(self, awaiting: list[AppStart], confirming: ConfirmingTerminals, deadline: float) -> bool:
        if self.clock.now() >= deadline:
            return False
        return len(still_waiting(awaiting)) > 0 or confirming.waiting

    @staticmethod
    def _still_without_window(placing: PlacingWindows, confirming: ConfirmingTerminals, starts: list[AppStart],
                              windows: list[Window]) -> list[AppStart]:
        unplaced = placing.place(placements_of(starts), windows)
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
            moved_on.append(start.next(self.clock.now()))
        return moved_on
