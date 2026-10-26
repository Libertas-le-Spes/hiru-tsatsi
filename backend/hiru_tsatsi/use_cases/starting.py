from hiru_tsatsi.use_cases import choosing_how_to_start
from hiru_tsatsi.use_cases.app_start import AppStart, placements_of, still_waiting, stopped_without_window
from hiru_tsatsi.use_cases.failures import AlreadyStarting
from hiru_tsatsi.use_cases.handover import Handover
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.learned_apps import LearnedApps
from hiru_tsatsi.use_cases.learned_during_start import save_learned
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Announcer, AppListStore, Clock, Desktop, OneStartAtATime, WindowNames
from hiru_tsatsi.use_cases.watching_starts import WatchingStarts
from hiru_tsatsi.work_apps.placement import Placement, names_of
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.windows import addresses_of


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
        learned = LearnedApps(apps)
        placing = PlacingWindows(self.desktop, self.names, learned, addresses_of(windows), self.recognising, set())
        missing = placing.place(apps.placements(), windows)
        already_open = list(placing.found)
        self._announce(missing)
        left = self.watching.until_placed(placing, self._begin_all(missing))
        save_learned(self.store, apps, learned.apps)
        stopped = placements_of(stopped_without_window(left))
        return Outcome(already_open=names_of(already_open), started=names_of(missing), moved=names_of(placing.moved),
                       unseen=names_of(placements_of(still_waiting(left))),
                       stopped_without_window=names_of(stopped),
                       for_the_offer=Handover(stopped, addresses_of(windows), set(placing.claimed)))

    def _announce(self, missing: list[Placement]) -> None:
        if missing:
            self.announcer.announce(names_of(missing))

    def _begin_all(self, missing: list[Placement]) -> list[AppStart]:
        starts = []
        for placement in missing:
            starts.append(choosing_how_to_start.begin(self.launcher, placement, self.clock.now(), self.recognising))
        return starts
