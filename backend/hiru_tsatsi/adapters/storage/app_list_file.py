from pathlib import Path
from typing import Callable, Sequence

from hiru_tsatsi.adapters.storage.app_list_format import from_saved, to_saved
from hiru_tsatsi.adapters.storage.files import Disk, Files
from hiru_tsatsi.adapters.storage.json_object import json_object, json_text
from hiru_tsatsi.work_apps.app_list import AppList

EarlierList = tuple[Path, Callable[[dict], AppList]]


class AppListFile:
    def __init__(self, path: Path, earlier: Sequence[EarlierList] = (), files: Files | None = None):
        if files is None:
            files = Disk()
        self.path = path
        self.earlier = earlier
        self.files = files
        self.read_before: str | None = None

    def load(self) -> AppList:
        if self.files.exists(self.path):
            self.read_before = self.files.read(self.path)
            return from_saved(json_object(self.read_before, self.path))
        self.read_before = ""
        return self._imported_from_earlier()

    def save(self, apps: AppList) -> None:
        text = json_text(to_saved(apps))
        self.files.write(self.path, text, read_before=self.read_before)
        self.read_before = text

    def _content(self, path: Path) -> dict:
        return json_object(self.files.read(path), path)

    def _imported_from_earlier(self) -> AppList:
        for place, reader in self.earlier:
            if self.files.exists(place):
                imported = reader(self._content(place))
                self.save(imported)
                return imported
        return AppList()
