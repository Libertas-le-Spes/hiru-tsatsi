from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.program_in_folder import ProgramInFolder
from hiru_tsatsi.work_apps.windows import Window, window_named, window_of_class


class Recognising:
    def __init__(self, home: str):
        self.home = home

    def known_window(self, app: App, windows: list[Window], claimed: set[str]) -> Window | None:
        running = self._window_running(app, windows, claimed)
        if running is not None:
            return running
        if app.in_terminal:
            return window_of_class(app.learned_window, windows, claimed)
        if app.knows_window:
            return window_named(app.learned_window, windows, claimed)
        return None

    def recognised_by_what_runs(self, app: App) -> bool:
        return self._program_in_folder(app) is not None

    def runs_inside(self, app: App, window: Window) -> bool:
        inside = self._program_in_folder(app)
        if inside is None:
            return False
        return inside.runs_in(window)

    def _window_running(self, app: App, windows: list[Window], claimed: set[str]) -> Window | None:
        for window in windows:
            if window.address not in claimed and self.runs_inside(app, window):
                return window
        return None

    def _program_in_folder(self, app: App) -> ProgramInFolder | None:
        return ProgramInFolder.of(app.command, self.home)
