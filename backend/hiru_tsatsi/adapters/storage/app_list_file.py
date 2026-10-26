import json
from pathlib import Path
from typing import Callable, Sequence

from hiru_tsatsi.adapters.storage.app_list_format import from_saved, to_saved
from hiru_tsatsi.adapters.storage.atomic_file import write_atomically
from hiru_tsatsi.work_apps.app_list import AppList


def _read(path: Path) -> dict:
    try:
        content = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(content, dict):
        return {}
    return content


EarlierList = tuple[Path, Callable[[dict], AppList]]


class AppListFile:
    def __init__(self, path: Path, earlier: Sequence[EarlierList] = ()):
        self.path = path
        self.earlier = earlier

    def load(self) -> AppList:
        if self.path.exists():
            return from_saved(_read(self.path))
        return self._imported_from_earlier()

    def save(self, apps: AppList) -> None:
        text = json.dumps(to_saved(apps), indent=2)
        write_atomically(self.path, text + "\n")

    def _imported_from_earlier(self) -> AppList:
        for place, reader in self.earlier:
            if place.exists():
                imported = reader(_read(place))
                self.save(imported)
                return imported
        return AppList()
