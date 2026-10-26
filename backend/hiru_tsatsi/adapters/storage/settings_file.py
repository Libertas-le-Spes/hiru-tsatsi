import json
from pathlib import Path

from hiru_tsatsi.adapters.storage.atomic_file import write_atomically

WINDOW_TITLES = "window_titles"


class SettingsFile:
    def __init__(self, path: Path):
        self.path = path

    def _read(self) -> dict:
        try:
            content = json.loads(self.path.read_text())
        except (OSError, json.JSONDecodeError):
            return {}
        return content if isinstance(content, dict) else {}

    def window_titles(self) -> bool | None:
        chosen = self._read().get(WINDOW_TITLES)
        return chosen if isinstance(chosen, bool) else None

    def set_window_titles(self, on: bool) -> None:
        settings = self._read()
        settings[WINDOW_TITLES] = on
        write_atomically(self.path, json.dumps(settings, indent=2) + "\n")
