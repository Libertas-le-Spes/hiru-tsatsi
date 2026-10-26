import argparse

from hiru_tsatsi.presenters.outcome_text import details, summary
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.wiring import Services


def report(services: Services, outcome: Outcome) -> int:
    print(summary(outcome))
    print(details(outcome))
    services.notifier.notify(summary(outcome), details(outcome))
    return 0


def start(services: Services, chosen: argparse.Namespace) -> int:
    return report(services, services.start.run())


def ask(services: Services, chosen: argparse.Namespace) -> int:
    outcome = services.ask.run()
    if outcome is None:
        return 0
    return report(services, outcome)
