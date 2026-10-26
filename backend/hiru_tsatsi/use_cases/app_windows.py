from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.windows import Window

Spot = tuple[int, int]


def windows_of(apps: AppList, windows: list[Window], recognising: Recognising) -> dict[Spot, Window]:
    claimed: set[str] = set()
    found: dict[Spot, Window] = {}
    for placement in apps.placements():
        window = recognising.known_window(placement.app, windows, claimed)
        if window is not None:
            claimed.add(window.address)
            found[(placement.workspace, placement.index)] = window
    return found


def unclaimed(apps: AppList, windows: list[Window], recognising: Recognising, keep: Spot | None = None) -> list[Window]:
    taken = set()
    for spot, window in windows_of(apps, windows, recognising).items():
        if spot != keep:
            taken.add(window.address)
    free = []
    for window in windows:
        if window.address not in taken:
            free.append(window)
    return free
