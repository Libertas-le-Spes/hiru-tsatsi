from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.workspace import Workspace


def app_list(*spaces: tuple[int, list[App]]) -> AppList:
    return AppList(tuple(Workspace(number, f"Space {number}", tuple(apps)) for number, apps in spaces))


class FakeStore:
    def __init__(self, apps: AppList):
        self.apps = apps
        self.saves = 0

    def load(self) -> AppList:
        return self.apps

    def save(self, apps: AppList) -> None:
        self.apps = apps
        self.saves += 1
