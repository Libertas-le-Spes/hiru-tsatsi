from typing import Callable

from hiru_tsatsi.entrypoints.cli.setting_commands import report_set_up
from hiru_tsatsi.use_cases.ports import DesktopNotSupported
from hiru_tsatsi.wiring import App


def set_up_desktop(opening: Callable[[], App]) -> int:
    try:
        app = opening()
    except DesktopNotSupported as unsupported:
        print(f"skipped:  the shortcut and the login question, as Hiru Tsatsi can't place windows on "
              f"{unsupported.desktop} yet; the command itself is installed")
        return 0
    return report_set_up(app)
