import os
from pathlib import Path


def _home(variable: str, fallback: str) -> Path:
    chosen = os.environ.get(variable)
    if chosen:
        return Path(chosen)
    return Path.home() / fallback


def config_home() -> Path:
    return _home("XDG_CONFIG_HOME", ".config")


def app_list_file() -> Path:
    return config_home() / "hiru-tsatsi" / "apps.json"


def installed_command() -> Path:
    return Path.home() / ".local" / "bin" / "hiru-tsatsi"


def window_names_folder() -> Path:
    return _home("XDG_STATE_HOME", ".local/state") / "window-names"


def settings_file() -> Path:
    return config_home() / "hiru-tsatsi" / "settings.json"


def workbench_list_file() -> Path:
    return config_home() / "workbench" / "apps.json"


def omastart_file() -> Path:
    return _home("XDG_STATE_HOME", ".local/state") / "omarchy" / "settings" / "omastart.json"
