import argparse
import sys
import webbrowser
from dataclasses import dataclass, field
from typing import Callable

from hiru_tsatsi.entrypoints.web import server
from hiru_tsatsi.presenters.outcome_text import details, not_supported, set_up_text, summary
from hiru_tsatsi.use_cases.ports import DesktopNotSupported, SetUpFailed
from hiru_tsatsi.use_cases.starting import Outcome
from hiru_tsatsi.wiring import App, open_app
from hiru_tsatsi.work_apps.app_list import Refused


@dataclass(frozen=True)
class Argument:
    name: str
    kind: type
    help: str


@dataclass(frozen=True)
class Command:
    run: Callable[[App, argparse.Namespace], int]
    help: str
    arguments: list[Argument] = field(default_factory=list)


def report(app: App, outcome: Outcome) -> int:
    print(summary(outcome))
    print(details(outcome))
    app.notifier.notify(summary(outcome), details(outcome))
    return 0


def start(app: App, chosen: argparse.Namespace) -> int:
    return report(app, app.start.run())


def ask(app: App, chosen: argparse.Namespace) -> int:
    outcome = app.ask.run()
    return report(app, outcome) if outcome else 0


def set_up(app: App, chosen: argparse.Namespace) -> int:
    try:
        print(set_up_text(app.set_up.run()))
    except SetUpFailed as failed:
        print(f"The desktop reported a problem after setting up, so check its config:\n{failed}")
        return 1
    return 0


def edit(app: App, chosen: argparse.Namespace) -> int:
    print(f"Editing your work apps at {server.page_url(server.PORT)}; it stops a few minutes after you close the page.")
    server.serve(app, app.page, webbrowser.open)
    return 0


def editing(change: Callable[[App, argparse.Namespace], object]) -> Callable[[App, argparse.Namespace], int]:
    def run(app: App, chosen: argparse.Namespace) -> int:
        try:
            change(app, chosen)
        except Refused as refused:
            print(refused, file=sys.stderr)
            return 1
        return 0
    return run


WORKSPACE = Argument("workspace", int, "the workspace's number")
INDEX = Argument("index", int, "the app's position in its workspace, starting at 0")

COMMANDS = {
    "start": Command(start, "start every work app that isn't open and put each window on its workspace"),
    "ask": Command(ask, "ask with a notification whether to start your work apps, and start them if you click it"),
    "edit": Command(edit, "open a page in your browser to edit your work apps and workspaces"),
    "add-workspace": Command(editing(lambda app, c: app.edit.add_workspace(c.workspace, c.label)),
                             "add a workspace with the number you choose",
                             [WORKSPACE, Argument("label", str, "its name")]),
    "remove-workspace": Command(editing(lambda app, c: app.edit.remove_workspace(c.workspace)),
                                "remove a workspace and its apps", [WORKSPACE]),
    "add-app": Command(editing(lambda app, c: app.edit.add_app(c.workspace, c.name, c.command)),
                       "add an app to a workspace",
                       [WORKSPACE, Argument("name", str, "what you call it"), Argument("command", str, "how to open it")]),
    "remove-app": Command(editing(lambda app, c: app.edit.remove_app(c.workspace, c.index)),
                          "remove an app from its workspace", [WORKSPACE, INDEX]),
    "set-up": Command(set_up, "add a shortcut that starts your work apps, and the question at login"),
}


def main(argv: list[str] | None = None, app: App | None = None, opening: Callable[[], App] = open_app) -> int:
    parser = argparse.ArgumentParser(prog="hiru-tsatsi", description="Open your work apps, each on its own workspace.")
    commands = parser.add_subparsers(dest="subcommand", required=True)
    for name, command in COMMANDS.items():
        sub = commands.add_parser(name, help=command.help)
        for argument in command.arguments:
            sub.add_argument(argument.name, type=argument.kind, help=argument.help)
    chosen = parser.parse_args(argv)
    try:
        return COMMANDS[chosen.subcommand].run(app or opening(), chosen)
    except DesktopNotSupported as refused:
        print(not_supported(refused.desktop))
        return 2
