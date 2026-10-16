import os
from pathlib import Path


def _home(variable: str, fallback: str) -> Path:
    return Path(os.environ.get(variable) or Path.home() / fallback)


def app_list_file() -> Path:
    return _home("XDG_CONFIG_HOME", ".config") / "workbench" / "apps.json"


def omastart_file() -> Path:
    return _home("XDG_STATE_HOME", ".local/state") / "omarchy" / "settings" / "omastart.json"
