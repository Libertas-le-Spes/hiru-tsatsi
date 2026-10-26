from hiru_tsatsi.use_cases import choosing_how_to_start
from hiru_tsatsi.use_cases.app_start import AppStart, placements_of, still_waiting, stopped_without_window
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.use_cases.failures import AlreadyStarting
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.learned_during_start import save_learned
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Announcer, AppListStore, Clock, Desktop, OneStartAtATime, WindowNames
from hiru_tsatsi.use_cases.watching_starts import WatchingStarts
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.windows import addresses_of


def _names(placements: list[Placement]) -> list[str]:
    names = []
    for placement in placements:
        names.append(placement.app.name)
    return names


class StartApps:
    def __init__(self, desktop: Desktop, launcher: Launcher, store: AppListStore, names: WindowNames,
                 announcer: Announcer, recognising: Recognising, watching: WatchingStarts, clock: Clock,
                 one_at_a_time: OneStartAtATime):
        self.desktop = desktop
        self.launcher = launcher
        self.store = store
        self.names = names
        self.announcer = announcer
        self.recognising = recognising
        self.watching = watching
        self.clock = clock
        self.one_at_a_time = one_at_a_time

    def run(self) -> Outcome:
        if not self.one_at_a_time.claimed():
            raise AlreadyStarting()
        apps = self.store.load()
        windows = self.desktop.windows()
        placing = PlacingWindows(self.desktop, self.names, apps, addresses_of(windows), self.recognising)
        missing = placing.place(apps.placements(), windows)
        already_open = list(placing.found)
        self._announce(missing)
        left = self.watching.until_placed(placing, ConfirmingTerminals(self.recognising), self._begin_all(missing))
        save_learned(self.store, apps, placing.apps)
        return Outcome(already_open=_names(already_open), started=_names(missing), moved=_names(placing.moved),
                       unseen=_names(placements_of(still_waiting(left))),
                       stopped_without_window=placements_of(stopped_without_window(left)))

    def _announce(self, missing: list[Placement]) -> None:
        if missing:
            self.announcer.announce(_names(missing))

    def _begin_all(self, missing: list[Placement]) -> list[AppStart]:
        starts = []
        for placement in missing:
            starts.append(choosing_how_to_start.begin(self.launcher, placement, self.clock.now(), self.recognising))
        return starts
