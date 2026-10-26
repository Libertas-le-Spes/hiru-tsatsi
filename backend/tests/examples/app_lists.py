from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.workspace import Workspace


def app_list(*spaces: tuple[int, list[App]]) -> AppList:
    workspaces = []
    for number, apps in spaces:
        workspaces.append(Workspace(number, f"Space {number}", tuple(apps)))
    return AppList(tuple(workspaces))
