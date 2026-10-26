import os
import shutil
from typing import Callable, Mapping, TypeVar

from hiru_tsatsi.adapters.desktops.hyprland import Hyprland
from hiru_tsatsi.adapters.desktops.hyprland_set_up import HyprlandSetUp
from hiru_tsatsi.adapters.storage import locations
from hiru_tsatsi.use_cases.ports import Desktop, DesktopNotSupported, DesktopSetUp

Found = TypeVar("Found")

DESKTOPS = [Hyprland.found]


def _hyprland_set_up(env: Mapping[str, str]) -> HyprlandSetUp | None:
    return HyprlandSetUp.found(env, locations.config_home())


SET_UPS = [_hyprland_set_up]


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


def set_up(env: Mapping[str, str] = os.environ) -> DesktopSetUp:
    return _first(SET_UPS, env)
