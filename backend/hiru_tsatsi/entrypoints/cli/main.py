import argparse
from typing import Callable

from hiru_tsatsi.entrypoints.cli.command_list import COMMANDS
from hiru_tsatsi.entrypoints.failure_report import STOPS, report_failure
from hiru_tsatsi.use_cases.services import Services


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
    except STOPS as failure:
        return report_failure(failure)
