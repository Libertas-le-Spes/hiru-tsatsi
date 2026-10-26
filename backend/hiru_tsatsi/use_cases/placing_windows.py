from hiru_tsatsi.use_cases.ports import Desktop, WindowNames
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.window_guessing import guess_window
from hiru_tsatsi.work_apps.window_naming import name_for
from hiru_tsatsi.work_apps.windows import Window


class PlacingWindows:
    def __init__(self, desktop: Desktop, names: WindowNames, apps: AppList, known_before: set[str],
                 recognising: Recognising):
        self.desktop = desktop
        self.names = names
        self.apps = apps
        self.known_before = known_before
        self.recognising = recognising
        self.claimed: set[str] = set()
        self.found: list[Placement] = []
        self.moved: list[Placement] = []
        self.in_terminal: list[Placement] = []

    def place(self, placements: list[Placement], windows: list[Window]) -> list[Placement]:
        unplaced = []
        for placement in self._known_ones_first(placements):
            if not self._placed(placement, windows):
                unplaced.append(placement)
        return unplaced

    def to_terminal(self, placement: Placement) -> Placement:
        self.apps = self.apps.with_terminal(placement)
        switched = self.apps.placement(placement.workspace, placement.index)
        self.in_terminal.append(switched)
        return switched

    @staticmethod
    def _known_ones_first(placements: list[Placement]) -> list[Placement]:
        known = []
        unknown = []
        for placement in placements:
            if placement.app.knows_window:
                known.append(placement)
            else:
                unknown.append(placement)
        return known + unknown

    def _placed(self, placement: Placement, windows: list[Window]) -> bool:
        window = self._find(placement, windows)
        if window is None:
            return False
        self.claimed.add(window.address)
        self.found.append(placement)
        self.names.record(window, placement.app.name)
        self._learn_its_window(placement, window, windows)
        self._move_to_its_workspace(placement, window)
        return True

    def _learn_its_window(self, placement: Placement, window: Window, windows: list[Window]) -> None:
        app = placement.app
        if app.knows_window or self.recognising.by_what_runs(app):
            return
        self.apps = self.apps.with_learned_window(placement, name_for(window, windows, app.command))

    def _move_to_its_workspace(self, placement: Placement, window: Window) -> None:
        if window.workspace == placement.workspace:
            return
        self.desktop.move(window, placement.workspace)
        self.moved.append(placement)

    def _find(self, placement: Placement, windows: list[Window]) -> Window | None:
        app = placement.app
        known = self.recognising.known_window(app, windows, self.claimed)
        if known is not None or app.knows_window:
            return known
        return guess_window(app.name, app.command, self._new_windows(windows))

    def _new_windows(self, windows: list[Window]) -> list[Window]:
        fresh = []
        for window in windows:
            if window.address not in self.known_before and window.address not in self.claimed:
                fresh.append(window)
        return fresh
