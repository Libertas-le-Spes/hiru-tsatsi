import argparse

from workbench.presenters.outcome_text import details, summary
from workbench.wiring import App, open_app


def start(app: App) -> int:
    outcome = app.start.run()
    print(summary(outcome))
    print(details(outcome))
    app.notifier.notify(summary(outcome), details(outcome))
    return 0


COMMANDS = {"start": (start, "start every work app that isn't open and put each window on its workspace")}


def main(argv: list[str] | None = None, app: App | None = None) -> int:
    parser = argparse.ArgumentParser(prog="workbench", description="Open your work apps, each on its own workspace.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, (_, help_text) in COMMANDS.items():
        commands.add_parser(name, help=help_text)
    chosen = parser.parse_args(argv)
    handler, _ = COMMANDS[chosen.command]
    return handler(app or open_app())
