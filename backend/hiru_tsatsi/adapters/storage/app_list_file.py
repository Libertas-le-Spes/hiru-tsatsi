import json
from pathlib import Path
from typing import Callable, Sequence

from hiru_tsatsi.adapters.storage.atomic_file import write_atomically
from hiru_tsatsi.work_apps.app_list import App, AppList, Workspace


def _read(path: Path) -> dict:
    try:
        content = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return content if isinstance(content, dict) else {}


def from_saved(content: dict) -> AppList:
    return AppList(tuple(
        Workspace(int(space["number"]), str(space.get("label", "")),
                  tuple(App(str(app["name"]), str(app["command"]), str(app.get("learned_window") or ""),
                            app.get("in_terminal") is True) for app in space.get("apps", [])))
        for space in content.get("workspaces", [])))


def from_omastart(content: dict) -> AppList:
    return AppList(tuple(
        Workspace(int(space["id"]), str(space.get("label", "")),
                  tuple(App(str(app["name"]), str(app["cmd"]), str(app.get("window") or "")) for app in space.get("apps", [])))
        for space in content.get("workspaces", [])))


def to_saved(apps: AppList) -> dict:
    return {"workspaces": [
        {"number": space.number, "label": space.label,
         "apps": [{"name": app.name, "command": app.command, "learned_window": app.learned_window,
                   "in_terminal": app.in_terminal} for app in space.apps]}
        for space in apps.workspaces]}


EarlierList = tuple[Path, Callable[[dict], AppList]]


class AppListFile:
    def __init__(self, path: Path, earlier: Sequence[EarlierList] = ()):
        self.path = path
        self.earlier = earlier

    def load(self) -> AppList:
        if self.path.exists():
            return from_saved(_read(self.path))
        found = next(((place, reader) for place, reader in self.earlier if place.exists()), None)
        if found is None:
            return AppList()
        place, reader = found
        imported = reader(_read(place))
        self.save(imported)
        return imported

    def save(self, apps: AppList) -> None:
        write_atomically(self.path, json.dumps(to_saved(apps), indent=2) + "\n")
