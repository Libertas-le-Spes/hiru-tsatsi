from pathlib import Path
from typing import Callable, Sequence

from hiru_tsatsi.adapters.storage.app_list_format import from_saved, to_saved
from hiru_tsatsi.adapters.storage.files import Files
from hiru_tsatsi.adapters.storage.json_object import json_object, json_text
from hiru_tsatsi.use_cases.failures import NotReadable
from hiru_tsatsi.work_apps.app_list import AppList

EarlierList = tuple[Path, Callable[[dict], AppList]]


class AppListFile:
    def __init__(self, path: Path, files: Files, earlier: Sequence[EarlierList] = ()):
        self.path = path
        self.earlier = earlier
        self.files = files
        self.read_before: str | None = None

    def load(self) -> AppList:
        if self.files.exists(self.path):
            self.read_before = self.files.read(self.path)
            return self._app_list(self.read_before, self.path, from_saved)
        self.read_before = ""
        return self._imported_from_earlier()

    def save(self, apps: AppList) -> None:
        text = json_text(to_saved(apps))
        self.files.write(self.path, text, read_before=self.read_before)
        self.read_before = text

    @staticmethod
    def _app_list(text: str, path: Path, reader: Callable[[dict], AppList]) -> AppList:
        content = json_object(text, path)
        try:
            return reader(content)
        except (KeyError, TypeError, ValueError, AttributeError) as wrong_shape:
            raise NotReadable(f"{path} is not an app list ({wrong_shape!r})") from wrong_shape

    def _imported_from_earlier(self) -> AppList:
        for place, reader in self.earlier:
            if self.files.exists(place):
                imported = self._app_list(self.files.read(place), place, reader)
                self.save(imported)
                return imported
        return AppList()
