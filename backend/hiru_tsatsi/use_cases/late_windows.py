from hiru_tsatsi.use_cases.learned_apps import LearnedApps
from hiru_tsatsi.use_cases.learned_during_start import save_learned
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import AppListStore, Desktop, WindowNames
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.windows import Window


class LateWindows:
    def __init__(self, desktop: Desktop, names: WindowNames, store: AppListStore, recognising: Recognising):
        self.desktop = desktop
        self.names = names
        self.store = store
        self.recognising = recognising

    def placed(self, placement: Placement, known_before: set[str], taken: set[str]) -> Window | None:
        apps = self.store.load()
        learned = LearnedApps(apps)
        placing = PlacingWindows(self.desktop, self.names, learned, known_before, self.recognising, taken)
        unplaced = placing.place([placement], self.desktop.windows())
        if unplaced:
            return None
        save_learned(self.store, apps, learned.apps)
        return placing.window_given_to(placement)
