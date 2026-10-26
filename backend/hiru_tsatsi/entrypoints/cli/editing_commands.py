import argparse
import sys
from typing import Callable

from hiru_tsatsi.wiring import Services
from hiru_tsatsi.work_apps.refusals import Refused

Change = Callable[[Services, argparse.Namespace], object]


class Editing:
    def __init__(self, change: Change):
        self.change = change

    def __call__(self, services: Services, chosen: argparse.Namespace) -> int:
        try:
            self.change(services, chosen)
        except Refused as refused:
            print(refused, file=sys.stderr)
            return 1
        return 0


def add_workspace(services: Services, chosen: argparse.Namespace) -> None:
    services.edit.add_workspace(chosen.workspace, chosen.label)


def change_workspace(services: Services, chosen: argparse.Namespace) -> None:
    services.edit.change_workspace(chosen.workspace, chosen.new_number, chosen.label)


def remove_workspace(services: Services, chosen: argparse.Namespace) -> None:
    services.edit.remove_workspace(chosen.workspace)


def add_app(services: Services, chosen: argparse.Namespace) -> None:
    services.edit.add_app(chosen.workspace, chosen.name, chosen.command)


def change_app(services: Services, chosen: argparse.Namespace) -> None:
    services.edit.change_app(chosen.workspace, chosen.index, chosen.name, chosen.command)


def remove_app(services: Services, chosen: argparse.Namespace) -> None:
    services.edit.remove_app(chosen.workspace, chosen.index)


def choose_window(services: Services, chosen: argparse.Namespace) -> None:
    services.edit.choose_window(chosen.workspace, chosen.index, chosen.address)


def forget_window(services: Services, chosen: argparse.Namespace) -> None:
    services.edit.forget_window(chosen.workspace, chosen.index)
