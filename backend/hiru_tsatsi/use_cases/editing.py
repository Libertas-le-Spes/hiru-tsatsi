from hiru_tsatsi.use_cases.app_windows import unclaimed
from hiru_tsatsi.use_cases.ports import AppListStore, Desktop
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.refusals import NothingThere
from hiru_tsatsi.work_apps.window_guessing import guess_window
from hiru_tsatsi.work_apps.window_naming import name_for
from hiru_tsatsi.work_apps.windows import Window


class EditAppList:
    def __init__(self, store: AppListStore, desktop: Desktop):
        self.store = store
        self.desktop = desktop

    def add_workspace(self, number: int, label: str) -> AppList:
        return self._saved(self.store.load().with_workspace(number, label))

    def change_workspace(self, number: int, new_number: int, label: str) -> AppList:
        return self._saved(self.store.load().with_workspace_changed(number, new_number, label))

    def remove_workspace(self, number: int) -> AppList:
        return self._saved(self.store.load().without_workspace(number))

    def add_app(self, workspace: int, name: str, command: str) -> AppList:
        apps = self.store.load()
        app = App(name, command, self._recognised(apps, name, command))
        return self._saved(apps.with_app(workspace, app))

    def change_app(self, workspace: int, index: int, name: str, command: str) -> AppList:
        return self._saved(self.store.load().with_app_changed(workspace, index, name, command))

    def remove_app(self, workspace: int, index: int) -> AppList:
        return self._saved(self.store.load().without_app(workspace, index))

    def choose_window(self, workspace: int, index: int, address: str) -> AppList:
        windows = self.desktop.windows()
        window = self._window_at(address, windows)
        apps = self.store.load()
        return self._saved(apps.with_learned_window(apps.placement(workspace, index), name_for(window, windows)))

    def forget_window(self, workspace: int, index: int) -> AppList:
        apps = self.store.load()
        return self._saved(apps.with_learned_window(apps.placement(workspace, index), ""))

    def _saved(self, changed: AppList) -> AppList:
        self.store.save(changed)
        return changed

    @staticmethod
    def _window_at(address: str, windows: list[Window]) -> Window:
        for window in windows:
            if window.address == address:
                return window
        raise NothingThere()

    def _recognised(self, apps: AppList, name: str, command: str) -> str:
        windows = self.desktop.windows()
        guessed = guess_window(name, command, unclaimed(apps, windows))
        if guessed is None:
            return ""
        return name_for(guessed, windows, command)
