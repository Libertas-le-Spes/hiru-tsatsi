from typing import Callable

from workbench.use_cases.overview import unclaimed
from workbench.use_cases.ports import AppListStore, Desktop
from workbench.work_apps.app_list import App, AppList, NothingThere
from workbench.work_apps.windows import guess_window, name_for


class EditAppList:
    def __init__(self, store: AppListStore, desktop: Desktop):
        self.store = store
        self.desktop = desktop

    def _change(self, change: Callable[[AppList], AppList]) -> AppList:
        changed = change(self.store.load())
        self.store.save(changed)
        return changed

    def add_workspace(self, number: int, label: str) -> AppList:
        return self._change(lambda apps: apps.with_workspace(number, label))

    def change_workspace(self, number: int, new_number: int, label: str) -> AppList:
        return self._change(lambda apps: apps.with_workspace_changed(number, new_number, label))

    def remove_workspace(self, number: int) -> AppList:
        return self._change(lambda apps: apps.without_workspace(number))

    def add_app(self, workspace: int, name: str, command: str) -> AppList:
        return self._change(lambda apps: apps.with_app(workspace, App(name, command, self._recognised(apps, name, command))))

    def change_app(self, workspace: int, index: int, name: str, command: str) -> AppList:
        return self._change(lambda apps: apps.with_app_changed(workspace, index, name, command))

    def remove_app(self, workspace: int, index: int) -> AppList:
        return self._change(lambda apps: apps.without_app(workspace, index))

    def choose_window(self, workspace: int, index: int, address: str) -> AppList:
        windows = self.desktop.windows()
        window = next((w for w in windows if w.address == address), None)
        if window is None:
            raise NothingThere()
        return self._change(lambda apps: apps.with_learned_window(apps.placement(workspace, index), name_for(window, windows)))

    def forget_window(self, workspace: int, index: int) -> AppList:
        return self._change(lambda apps: apps.with_learned_window(apps.placement(workspace, index), ""))

    def _recognised(self, apps: AppList, name: str, command: str) -> str:
        windows = self.desktop.windows()
        guessed = guess_window(name, command, unclaimed(apps, windows))
        return name_for(guessed, windows, command) if guessed else ""
