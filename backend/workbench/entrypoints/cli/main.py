import argparse
import webbrowser
from typing import Callable

from workbench.entrypoints.web import server
from workbench.presenters.outcome_text import details, not_supported, set_up_text, summary
from workbench.use_cases.ports import DesktopNotSupported, SetUpFailed
from workbench.use_cases.starting import Outcome
from workbench.wiring import App, open_app


def report(app: App, outcome: Outcome) -> int:
    print(summary(outcome))
    print(details(outcome))
    app.notifier.notify(summary(outcome), details(outcome))
    return 0


def start(app: App) -> int:
    return report(app, app.start.run())


def ask(app: App) -> int:
    outcome = app.ask.run()
    return report(app, outcome) if outcome else 0


def set_up(app: App) -> int:
    try:
        print(set_up_text(app.set_up.run()))
    except SetUpFailed as failed:
        print(f"The desktop reported a problem after setting up, so check its config:\n{failed}")
        return 1
    return 0


def edit(app: App) -> int:
    print(f"Editing your work apps at {server.page_url(server.PORT)}; it stops a few minutes after you close the page.")
    server.serve(app, app.page, webbrowser.open)
    return 0


COMMANDS = {
    "start": (start, "start every work app that isn't open and put each window on its workspace"),
    "ask": (ask, "ask with a notification whether to start your work apps, and start them if you click it"),
    "edit": (edit, "open a page in your browser to edit your work apps and workspaces"),
    "set-up": (set_up, "add a shortcut that starts your work apps, and the question at login"),
}


def main(argv: list[str] | None = None, app: App | None = None, opening: Callable[[], App] = open_app) -> int:
    parser = argparse.ArgumentParser(prog="workbench", description="Open your work apps, each on its own workspace.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, (_, help_text) in COMMANDS.items():
        commands.add_parser(name, help=help_text)
    chosen = parser.parse_args(argv)
    handler, _ = COMMANDS[chosen.command]
    try:
        return handler(app or opening())
    except DesktopNotSupported as refused:
        print(not_supported(refused.desktop))
        return 2
