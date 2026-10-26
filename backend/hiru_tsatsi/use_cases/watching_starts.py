from typing import Callable

from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Desktop
from hiru_tsatsi.work_apps.placement import Placement

POLL_SECONDS = 0.5


class WatchingStarts:
    def __init__(self, desktop: Desktop, clock: Callable[[], float], wait: Callable[[float], None],
                 watch_seconds: float):
        self.desktop = desktop
        self.clock = clock
        self.wait = wait
        self.watch_seconds = watch_seconds

    def until_placed(self, placing: PlacingWindows, started: list[Placement]) -> list[Placement]:
        deadline = self.clock() + self.watch_seconds
        awaiting = started
        while awaiting and self.clock() < deadline:
            self.wait(POLL_SECONDS)
            awaiting = placing.place(awaiting, self.desktop.windows())
        return awaiting
