import sys
from typing import Callable

from hiru_tsatsi.entrypoints.failure_report import STOPS, report_failure
from hiru_tsatsi.entrypoints.install.linking import link_commands
from hiru_tsatsi.entrypoints.install.setting_up import set_up_desktop
from hiru_tsatsi.use_cases.installing import LinkCommands
from hiru_tsatsi.use_cases.services import Services


def install(argv: list[str], linking_for: Callable[[str, str], LinkCommands], opening: Callable[[], Services]) -> int:
    if len(argv) != 2:
        print("usage: python3 -P -m hiru_tsatsi.entrypoints.install <bin folder> <launcher>", file=sys.stderr)
        return 2
    bin_dir = argv[0]
    launcher = argv[1]
    try:
        link_commands(linking_for(bin_dir, launcher))
        return set_up_desktop(opening)
    except STOPS as failure:
        return report_failure(failure)
