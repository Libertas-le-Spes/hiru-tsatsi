from pathlib import Path

from hiru_tsatsi.adapters.storage.files import Disk, Files
from hiru_tsatsi.adapters.storage.json_object import json_object, json_text

WINDOW_TITLES = "window_titles"


class SettingsFile:
    def __init__(self, path: Path, files: Files = Disk()):
        self.path = path
        self.files = files

    def window_titles(self) -> bool | None:
        chosen = self._settings().get(WINDOW_TITLES)
        if not isinstance(chosen, bool):
            return None
        return chosen

    def set_window_titles(self, on: bool) -> None:
        settings = self._settings()
        settings[WINDOW_TITLES] = on
        self.files.write(self.path, json_text(settings))

    def _settings(self) -> dict:
        return json_object(self.files.read(self.path))
