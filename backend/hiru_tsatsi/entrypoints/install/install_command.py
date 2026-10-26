import sys
from typing import Callable

from hiru_tsatsi.entrypoints.install.linking import link_commands
from hiru_tsatsi.entrypoints.install.setting_up import set_up_desktop
from hiru_tsatsi.use_cases.installing import LinkCommands
from hiru_tsatsi.wiring import Services


def install(argv: list[str], linking_for: Callable[[str, str], LinkCommands], opening: Callable[[], Services]) -> int:
    if len(argv) != 2:
        print("usage: python3 -P -m hiru_tsatsi.entrypoints.install <bin folder> <launcher>", file=sys.stderr)
        return 2
    bin_dir = argv[0]
    launcher = argv[1]
    linked = link_commands(linking_for(bin_dir, launcher))
    if linked != 0:
        return linked
    return set_up_desktop(opening)
