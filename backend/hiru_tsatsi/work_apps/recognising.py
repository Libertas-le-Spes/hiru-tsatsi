from typing import Callable

from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.program_in_folder import ProgramInFolder
from hiru_tsatsi.work_apps.shells import SHELLS
from hiru_tsatsi.work_apps.windows import Window, window_named, window_of_class


def without_waiting_shells(windows: list[Window]) -> list[Window]:
    alive = []
    for window in windows:
        if window.program not in SHELLS:
            alive.append(window)
    return alive


class Recognising:
    def __init__(self, home: str, real_folder: Callable[[str], str]):
        self.home = home
        self.real_folder = real_folder
        self.read_commands: dict[str, ProgramInFolder | None] = {}

    def known_window(self, app: App, windows: list[Window], claimed: set[str]) -> Window | None:
        running = self._window_running(app, windows, claimed)
        if running is not None:
            return running
        if self.is_terminal_app(app):
            return window_of_class(app.learned_window, without_waiting_shells(windows), claimed)
        if app.knows_window:
            return window_named(app.learned_window, self.could_be_its_windows(app, windows), claimed)
        return None

    def could_be_its_windows(self, app: App, windows: list[Window]) -> list[Window]:
        possible = []
        for window in windows:
            if self._could_be_its_window(app, window):
                possible.append(window)
        return possible

    def _could_be_its_window(self, app: App, window: Window) -> bool:
        inside = self._program_in_folder(app)
        if inside is None:
            return True
        return not inside.runs_elsewhere_in(window)

    def is_terminal_app(self, app: App) -> bool:
        return app.opens_in_terminal and self.has_program_in_folder(app)

    def has_program_in_folder(self, app: App) -> bool:
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
        if app.command not in self.read_commands:
            self.read_commands[app.command] = self._read(app.command)
        return self.read_commands[app.command]

    def _read(self, command: str) -> ProgramInFolder | None:
        inside = ProgramInFolder.of(command, self.home)
        if inside is None:
            return None
        return inside.leading_to(self.real_folder)
