import argparse
import sys
from typing import Callable

from hiru_tsatsi.wiring import App
from hiru_tsatsi.work_apps.refusals import Refused

Change = Callable[[App, argparse.Namespace], object]


class Editing:
    def __init__(self, change: Change):
        self.change = change

    def __call__(self, app: App, chosen: argparse.Namespace) -> int:
        try:
            self.change(app, chosen)
        except Refused as refused:
            print(refused, file=sys.stderr)
            return 1
        return 0


def add_workspace(app: App, chosen: argparse.Namespace) -> None:
    app.edit.add_workspace(chosen.workspace, chosen.label)


def change_workspace(app: App, chosen: argparse.Namespace) -> None:
    app.edit.change_workspace(chosen.workspace, chosen.new_number, chosen.label)


def remove_workspace(app: App, chosen: argparse.Namespace) -> None:
    app.edit.remove_workspace(chosen.workspace)


def add_app(app: App, chosen: argparse.Namespace) -> None:
    app.edit.add_app(chosen.workspace, chosen.name, chosen.command)


def change_app(app: App, chosen: argparse.Namespace) -> None:
    app.edit.change_app(chosen.workspace, chosen.index, chosen.name, chosen.command)


def remove_app(app: App, chosen: argparse.Namespace) -> None:
    app.edit.remove_app(chosen.workspace, chosen.index)


def choose_window(app: App, chosen: argparse.Namespace) -> None:
    app.edit.choose_window(chosen.workspace, chosen.index, chosen.address)


def forget_window(app: App, chosen: argparse.Namespace) -> None:
    app.edit.forget_window(chosen.workspace, chosen.index)
