import json
import os
import tempfile
from pathlib import Path

from workbench.work_apps.app_list import App, AppList, Workspace


def _read(path: Path) -> dict:
    try:
        content = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return content if isinstance(content, dict) else {}


def from_saved(content: dict) -> AppList:
    return AppList(tuple(
        Workspace(int(space["number"]), str(space.get("label", "")),
                  tuple(App(str(app["name"]), str(app["command"]), str(app.get("learned_window") or "")) for app in space.get("apps", [])))
        for space in content.get("workspaces", [])))


def from_omastart(content: dict) -> AppList:
    return AppList(tuple(
        Workspace(int(space["id"]), str(space.get("label", "")),
                  tuple(App(str(app["name"]), str(app["cmd"]), str(app.get("window") or "")) for app in space.get("apps", [])))
        for space in content.get("workspaces", [])))


def to_saved(apps: AppList) -> dict:
    return {"workspaces": [
        {"number": space.number, "label": space.label,
         "apps": [{"name": app.name, "command": app.command, "learned_window": app.learned_window} for app in space.apps]}
        for space in apps.workspaces]}


class AppListFile:
    def __init__(self, path: Path, omastart: Path):
        self.path = path
        self.omastart = omastart

    def load(self) -> AppList:
        if self.path.exists():
            return from_saved(_read(self.path))
        return from_omastart(_read(self.omastart))

    def save(self, apps: AppList) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(dir=self.path.parent, prefix=".apps-")
        with os.fdopen(handle, "w") as file:
            json.dump(to_saved(apps), file, indent=2)
            file.write("\n")
        os.replace(temporary, self.path)
