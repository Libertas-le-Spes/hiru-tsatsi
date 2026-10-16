from typing import Callable

from hiru_tsatsi.use_cases.ports import SettingsStore, WindowNames
from hiru_tsatsi.work_apps.windows import Window


class WindowTitles:
    def __init__(self, settings: SettingsStore, namer_installed: Callable[[], bool]):
        self.settings = settings
        self.namer_installed = namer_installed

    def wanted(self) -> bool:
        chosen = self.settings.window_titles()
        return self.namer_installed() if chosen is None else chosen

    def chosen(self) -> bool:
        return self.settings.window_titles() is not None

    def turn(self, on: bool) -> None:
        self.settings.set_window_titles(on)


class NamesWhenWanted:
    def __init__(self, titles: WindowTitles, names: WindowNames):
        self.titles = titles
        self.names = names

    def record(self, window: Window, name: str) -> None:
        if self.titles.wanted():
            self.names.record(window, name)
