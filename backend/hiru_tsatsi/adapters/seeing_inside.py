from dataclasses import replace
from typing import Callable

from hiru_tsatsi.use_cases.ports import Desktop
from hiru_tsatsi.work_apps.windows import Window

WhatRuns = Callable[[int], tuple[str, str]]


def _shared_pids(windows: list[Window]) -> set[int]:
    seen = set()
    shared = set()
    for window in windows:
        if window.pid in seen:
            shared.add(window.pid)
        seen.add(window.pid)
    return shared


class SeeingInside:
    def __init__(self, desktop: Desktop, what_runs: WhatRuns):
        self.desktop = desktop
        self.what_runs = what_runs

    def windows(self) -> list[Window]:
        listed = self.desktop.windows()
        shared = _shared_pids(listed)
        seen = []
        for window in listed:
            seen.append(self._looked_inside(window, shared))
        return seen

    def launch(self, command: str, workspace: int) -> None:
        self.desktop.launch(command, workspace)

    def move(self, window: Window, workspace: int) -> None:
        self.desktop.move(window, workspace)

    def _looked_inside(self, window: Window, shared: set[int]) -> Window:
        if window.pid <= 0 or window.pid in shared:
            return window
        program, folder = self.what_runs(window.pid)
        return replace(window, program=program, folder=folder)
