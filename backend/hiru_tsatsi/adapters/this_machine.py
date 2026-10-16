import os
import shutil
from typing import Callable, Mapping, TypeVar

from hiru_tsatsi.adapters.desktops.hyprland import Hyprland
from hiru_tsatsi.adapters.desktops.hyprland_set_up import HyprlandSetUp
from hiru_tsatsi.adapters.storage import locations
from hiru_tsatsi.use_cases.ports import Desktop, DesktopNotSupported, DesktopSetUp

Found = TypeVar("Found")

DESKTOPS = [Hyprland.found]
SET_UPS = [lambda env: HyprlandSetUp.found(env, locations.config_home())]


def _first(finders: list[Callable[[Mapping[str, str]], Found | None]], env: Mapping[str, str]) -> Found:
    found = next((f for finder in finders if (f := finder(env)) is not None), None)
    if found is None:
        raise DesktopNotSupported(env.get("XDG_CURRENT_DESKTOP") or env.get("XDG_SESSION_DESKTOP") or "this desktop")
    return found


def window_namer_installed() -> bool:
    return shutil.which("window-names") is not None


def desktop(env: Mapping[str, str] = os.environ) -> Desktop:
    return _first(DESKTOPS, env)


def set_up(env: Mapping[str, str] = os.environ) -> DesktopSetUp:
    return _first(SET_UPS, env)
