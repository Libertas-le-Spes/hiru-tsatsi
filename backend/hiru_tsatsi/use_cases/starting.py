from typing import Callable

from hiru_tsatsi.use_cases import app_starts
from hiru_tsatsi.use_cases.app_starts import AppStart
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Announcer, AppListStore, Desktop, WindowNames
from hiru_tsatsi.use_cases.watching_starts import WatchingStarts
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.windows import Window

WATCH_SECONDS = 60.0


def _names(placements: list[Placement]) -> list[str]:
    names = []
    for placement in placements:
        names.append(placement.app.name)
    return names


def _addresses(windows: list[Window]) -> set[str]:
    addresses = set()
    for window in windows:
        addresses.add(window.address)
    return addresses


class StartApps:
    def __init__(self, desktop: Desktop, store: AppListStore, names: WindowNames, clock: Callable[[], float],
                 wait: Callable[[float], None], announcer: Announcer, recognising: Recognising,
                 watch_seconds: float = WATCH_SECONDS):
        self.desktop = desktop
        self.store = store
        self.names = names
        self.clock = clock
        self.announcer = announcer
        self.recognising = recognising
        self.watching = WatchingStarts(desktop, clock, wait, watch_seconds)

    def run(self) -> Outcome:
        apps = self.store.load()
        windows = self.desktop.windows()
        placing = PlacingWindows(self.desktop, self.names, apps, _addresses(windows), self.recognising)
        missing = placing.place(apps.placements(), windows)
        already_open = list(placing.found)
        self._announce(missing)
        unseen = self.watching.until_placed(placing, self._begin_all(missing))
        if placing.apps != apps:
            self.store.save(placing.apps)
        return Outcome(_names(already_open), _names(missing), _names(placing.moved), _names(unseen),
                       _names(placing.in_terminal))

    def _announce(self, missing: list[Placement]) -> None:
        if missing:
            self.announcer.announce(_names(missing))

    def _begin_all(self, missing: list[Placement]) -> list[AppStart]:
        starts = []
        for placement in missing:
            starts.append(app_starts.begin(self.desktop, placement, self.clock()))
        return starts
