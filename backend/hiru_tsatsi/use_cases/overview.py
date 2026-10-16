from dataclasses import dataclass

from hiru_tsatsi.use_cases.ports import AppListStore, Desktop
from hiru_tsatsi.work_apps.app_list import AppList, Placement
from hiru_tsatsi.work_apps.windows import Window, likeliest_first, window_named


@dataclass(frozen=True)
class AppView:
    placement: Placement
    window: Window | None


@dataclass(frozen=True)
class WorkspaceView:
    number: int
    label: str
    apps: list[AppView]


def windows_of(apps: AppList, windows: list[Window]) -> dict[tuple[int, int], Window]:
    claimed: set[str] = set()
    found: dict[tuple[int, int], Window] = {}
    for placement in apps.placements():
        window = window_named(placement.app.learned_window, windows, claimed) if placement.app.knows_window else None
        if window:
            claimed.add(window.address)
            found[(placement.workspace, placement.index)] = window
    return found


def unclaimed(apps: AppList, windows: list[Window], keep: tuple[int, int] | None = None) -> list[Window]:
    taken = {w.address for key, w in windows_of(apps, windows).items() if key != keep}
    return [w for w in windows if w.address not in taken]


class Overview:
    def __init__(self, store: AppListStore, desktop: Desktop):
        self.store = store
        self.desktop = desktop

    def run(self) -> list[WorkspaceView]:
        apps = self.store.load()
        found = windows_of(apps, self.desktop.windows())
        return [WorkspaceView(space.number, space.label,
                              [AppView(Placement(space.number, index, app), found.get((space.number, index)))
                               for index, app in enumerate(space.apps)])
                for space in apps.workspaces]

    def candidates(self, workspace: int, index: int) -> list[Window]:
        apps = self.store.load()
        app = apps.placement(workspace, index).app
        return likeliest_first(app.name, app.command, unclaimed(apps, self.desktop.windows(), (workspace, index)))
