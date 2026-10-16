import json
import os
import tempfile
from pathlib import Path

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
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(dir=self.path.parent, prefix=".settings-")
        with os.fdopen(handle, "w") as file:
            json.dump(settings, file, indent=2)
            file.write("\n")
        os.replace(temporary, self.path)
