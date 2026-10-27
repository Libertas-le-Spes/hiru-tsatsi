from hiru_tsatsi.use_cases.learned_apps import LearnedApps
from hiru_tsatsi.use_cases.learned_during_start import save_learned
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import AppListStore, Desktop, WindowNames
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising, without_waiting_shells
from hiru_tsatsi.work_apps.windows import Window, addresses_of


class LateWindows:
    def __init__(self, desktop: Desktop, names: WindowNames, store: AppListStore, recognising: Recognising):
        self.desktop = desktop
        self.names = names
        self.store = store
        self.recognising = recognising

    def placed(self, placement: Placement, taken: set[str]) -> Window | None:
        apps = self.store.load()
        learned = LearnedApps(apps)
        windows = without_waiting_shells(self.desktop.windows())
        nothing_guessed = addresses_of(windows)
        placing = PlacingWindows(self.desktop, self.names, learned, nothing_guessed, self.recognising, taken)
        unplaced = placing.place([placement], windows)
        if unplaced:
            return None
        save_learned(self.store, apps, learned.apps)
        return placing.window_given_to(placement)
