import sys
from typing import Callable

from hiru_tsatsi.use_cases.installing import LinkCommands, NotOurs


def link_commands(linking: LinkCommands) -> int:
    try:
        linked = linking.run()
    except NotOurs as refused:
        print(f"hiru-tsatsi install: {refused.path} is already there and is not Hiru Tsatsi; "
              "move it away and run install.sh again", file=sys.stderr)
        return 1
    if linked.retired is not None:
        print(f"removed:  {linked.retired}, the old short name; type 'tsatsi' now")
    print(f"command:  {linked.command}, and {linked.short} for short")
    return 0


def main(argv: list[str], opening: Callable[[str, str], LinkCommands]) -> int:
    bin_dir = argv[0]
    launcher = argv[1]
    return link_commands(opening(bin_dir, launcher))
