from dataclasses import dataclass

from hiru_tsatsi.use_cases.app_windows import Spot, unclaimed, windows_of
from hiru_tsatsi.use_cases.ports import AppListStore, Desktop
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.window_guessing import likeliest_first
from hiru_tsatsi.work_apps.windows import Window


@dataclass(frozen=True)
class AppView:
    placement: Placement
    window: Window | None


@dataclass(frozen=True)
class WorkspaceView:
    number: int
    label: str
    apps: list[AppView]


class Overview:
    def __init__(self, store: AppListStore, desktop: Desktop):
        self.store = store
        self.desktop = desktop

    def run(self) -> list[WorkspaceView]:
        apps = self.store.load()
        found = windows_of(apps, self.desktop.windows())
        views = []
        for space in apps.workspaces:
            views.append(WorkspaceView(space.number, space.label, self._app_views(space.number, space.apps, found)))
        return views

    def candidates(self, workspace: int, index: int) -> list[Window]:
        apps = self.store.load()
        app = apps.placement(workspace, index).app
        free = unclaimed(apps, self.desktop.windows(), (workspace, index))
        return likeliest_first(app.name, app.command, free)

    @staticmethod
    def _app_views(number: int, apps: tuple[App, ...], found: dict[Spot, Window]) -> list[AppView]:
        views = []
        for index, app in enumerate(apps):
            views.append(AppView(Placement(number, index, app), found.get((number, index))))
        return views
