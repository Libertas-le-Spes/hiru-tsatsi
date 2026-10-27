from typing import Protocol

from hiru_tsatsi.work_apps.placement import Placement


class AppStart(Protocol):
    placement: Placement
    waits_for_window: bool

    def next(self, now: float) -> "AppStart": ...


def placements_of(starts: list[AppStart]) -> list[Placement]:
    placements = []
    for start in starts:
        placements.append(start.placement)
    return placements


def still_waiting(starts: list[AppStart]) -> list[AppStart]:
    waiting = []
    for start in starts:
        if start.waits_for_window:
            waiting.append(start)
    return waiting


def stopped_without_window(starts: list[AppStart]) -> list[AppStart]:
    stopped = []
    for start in starts:
        if not start.waits_for_window:
            stopped.append(start)
    return stopped
