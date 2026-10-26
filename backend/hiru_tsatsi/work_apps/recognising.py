from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.program_in_folder import ProgramInFolder
from hiru_tsatsi.work_apps.windows import Window, window_named


class Recognising:
    def __init__(self, home: str):
        self.home = home

    def known_window(self, app: App, windows: list[Window], claimed: set[str]) -> Window | None:
        running = self.window_running(app, windows, claimed)
        if running is not None:
            return running
        if app.knows_window:
            return window_named(app.learned_window, windows, claimed)
        return None

    def window_running(self, app: App, windows: list[Window], claimed: set[str]) -> Window | None:
        inside = self.program_in_folder(app)
        if inside is None:
            return None
        for window in windows:
            if window.address not in claimed and inside.runs_in(window):
                return window
        return None

    def by_what_runs(self, app: App) -> bool:
        return self.program_in_folder(app) is not None

    def program_in_folder(self, app: App) -> ProgramInFolder | None:
        return ProgramInFolder.of(app.command, self.home)
