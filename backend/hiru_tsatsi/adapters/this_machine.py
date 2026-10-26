import os
import shutil
from pathlib import Path
from typing import Callable, Mapping, TypeVar

from hiru_tsatsi.adapters.desktops.hyprland import Hyprland
from hiru_tsatsi.adapters.desktops.hyprland_set_up import HyprlandSetUp
from hiru_tsatsi.adapters.storage.files import Files
from hiru_tsatsi.use_cases.failures import DesktopNotSupported
from hiru_tsatsi.use_cases.ports import Desktop, DesktopSetUp

Found = TypeVar("Found")

DESKTOPS = [Hyprland.found]
SET_UPS = [HyprlandSetUp.found]


def _desktop_name(env: Mapping[str, str]) -> str:
    for variable in ("XDG_CURRENT_DESKTOP", "XDG_SESSION_DESKTOP"):
        if env.get(variable):
            return env[variable]
    return "this desktop"


def _first(finders: list[Callable[[Mapping[str, str]], Found | None]], env: Mapping[str, str]) -> Found:
    for finder in finders:
        found = finder(env)
        if found is not None:
            return found
    raise DesktopNotSupported(_desktop_name(env))


def window_namer_installed() -> bool:
    return shutil.which("window-names") is not None


def desktop(env: Mapping[str, str] = os.environ) -> Desktop:
    return _first(DESKTOPS, env)


def set_up(config_home: Path, files: Files, env: Mapping[str, str] = os.environ) -> DesktopSetUp:
    for finder in SET_UPS:
        found = finder(env, config_home, files)
        if found is not None:
            return found
    raise DesktopNotSupported(_desktop_name(env))
