from typing import Callable

from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.workspace import Workspace


def _text(value) -> str:
    if value is None:
        return ""
    return str(value)


def _saved_app(app: dict) -> App:
    return App(str(app["name"]), str(app["command"]), _text(app.get("learned_window")), app.get("in_terminal") is True,
               app.get("terminal_ruled_out") is True)


def _omastart_app(app: dict) -> App:
    return App(str(app["name"]), str(app["cmd"]), _text(app.get("window")))


def _workspace(number: int, space: dict, read_app: Callable[[dict], App]) -> Workspace:
    apps = []
    for app in space.get("apps", []):
        apps.append(read_app(app))
    return Workspace(number, str(space.get("label", "")), tuple(apps))


def from_saved(content: dict) -> AppList:
    workspaces = []
    for space in content.get("workspaces", []):
        workspaces.append(_workspace(int(space["number"]), space, _saved_app))
    return AppList(tuple(workspaces))


def from_omastart(content: dict) -> AppList:
    workspaces = []
    for space in content.get("workspaces", []):
        workspaces.append(_workspace(int(space["id"]), space, _omastart_app))
    return AppList(tuple(workspaces))


def _app_to_save(app: App) -> dict:
    return {"name": app.name, "command": app.command, "learned_window": app.learned_window,
            "in_terminal": app.opens_in_terminal, "terminal_ruled_out": app.terminal_ruled_out}


def _workspace_to_save(space: Workspace) -> dict:
    apps = []
    for app in space.apps:
        apps.append(_app_to_save(app))
    return {"number": space.number, "label": space.label, "apps": apps}


def to_saved(apps: AppList) -> dict:
    workspaces = []
    for space in apps.workspaces:
        workspaces.append(_workspace_to_save(space))
    return {"workspaces": workspaces}
