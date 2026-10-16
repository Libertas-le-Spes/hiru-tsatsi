import os
from typing import Mapping

from workbench.adapters.desktops.hyprland import Hyprland
from workbench.use_cases.ports import Desktop, DesktopNotSupported

DESKTOPS = [Hyprland]


def desktop(env: Mapping[str, str] = os.environ) -> Desktop:
    found = next((d for kind in DESKTOPS if (d := kind.found(env)) is not None), None)
    if found is None:
        raise DesktopNotSupported(env.get("XDG_CURRENT_DESKTOP") or env.get("XDG_SESSION_DESKTOP") or "this desktop")
    return found
