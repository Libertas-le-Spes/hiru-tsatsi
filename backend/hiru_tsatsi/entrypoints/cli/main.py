import argparse
import sys
from typing import Callable

from hiru_tsatsi.entrypoints.cli.command_list import COMMANDS
from hiru_tsatsi.presenters.unsupported_desktop import not_supported
from hiru_tsatsi.use_cases.failures import DesktopNotSupported, NotReadable, NotSaved
from hiru_tsatsi.use_cases.services import Services
from hiru_tsatsi.work_apps.refusals import Refused


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hiru-tsatsi", description="Open your work apps, each on its own workspace.")
    commands = parser.add_subparsers(dest="subcommand", required=True)
    for name, command in COMMANDS.items():
        sub = commands.add_parser(name, help=command.help)
        for argument in command.arguments:
            sub.add_argument(argument.name, type=argument.kind, help=argument.help, choices=argument.choices,
                             nargs=argument.how_many())
    return parser


def main(argv: list[str], opening: Callable[[], Services]) -> int:
    chosen = parser().parse_args(argv)
    try:
        return COMMANDS[chosen.subcommand].run(opening(), chosen)
    except DesktopNotSupported as refused:
        print(not_supported(refused.desktop))
        return 2
    except NotSaved as refused:
        print(f"Nothing was saved: {refused}.", file=sys.stderr)
        return 1
    except NotReadable as unreadable:
        print(f"Nothing was changed: {unreadable}.", file=sys.stderr)
        return 1
    except Refused as refused:
        print(refused, file=sys.stderr)
        return 1
