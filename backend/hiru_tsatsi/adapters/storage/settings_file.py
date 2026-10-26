from pathlib import Path

from hiru_tsatsi.adapters.storage.files import Files
from hiru_tsatsi.adapters.storage.json_object import json_object, json_text
from hiru_tsatsi.use_cases.failures import NotReadable

WINDOW_TITLES = "window_titles"


class SettingsFile:
    def __init__(self, path: Path, files: Files):
        self.path = path
        self.files = files

    def window_titles(self) -> bool | None:
        try:
            chosen = self._settings().get(WINDOW_TITLES)
        except NotReadable:
            return None
        if not isinstance(chosen, bool):
            return None
        return chosen

    def set_window_titles(self, on: bool) -> None:
        settings = self._settings()
        settings[WINDOW_TITLES] = on
        self.files.write(self.path, json_text(settings))

    def _settings(self) -> dict:
        return json_object(self.files.read(self.path), self.path)
