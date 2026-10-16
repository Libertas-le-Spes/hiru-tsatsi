import os
from typing import Mapping

from workbench.adapters.desktops.hyprland import Hyprland
from workbench.adapters.desktops.launch_only import LaunchOnly
from workbench.use_cases.ports import Desktop

DESKTOPS = [Hyprland, LaunchOnly]


def desktop(env: Mapping[str, str] = os.environ) -> Desktop:
    return next(found for kind in DESKTOPS if (found := kind.found(env)) is not None)
