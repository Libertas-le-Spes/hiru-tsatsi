import argparse

from hiru_tsatsi.presenters.outcome_text import details, summary
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.wiring import App


def report(app: App, outcome: Outcome) -> int:
    print(summary(outcome))
    print(details(outcome))
    app.notifier.notify(summary(outcome), details(outcome))
    return 0


def start(app: App, chosen: argparse.Namespace) -> int:
    return report(app, app.start.run())


def ask(app: App, chosen: argparse.Namespace) -> int:
    outcome = app.ask.run()
    if outcome is None:
        return 0
    return report(app, outcome)
