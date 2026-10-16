import os
from pathlib import Path


def _home(variable: str, fallback: str) -> Path:
    return Path(os.environ.get(variable) or Path.home() / fallback)


def config_home() -> Path:
    return _home("XDG_CONFIG_HOME", ".config")


def app_list_file() -> Path:
    return config_home() / "workbench" / "apps.json"


def installed_command() -> Path:
    return Path.home() / ".local" / "bin" / "workbench"


def window_names_folder() -> Path:
    return _home("XDG_STATE_HOME", ".local/state") / "window-names"


def omastart_file() -> Path:
    return _home("XDG_STATE_HOME", ".local/state") / "omarchy" / "settings" / "omastart.json"
