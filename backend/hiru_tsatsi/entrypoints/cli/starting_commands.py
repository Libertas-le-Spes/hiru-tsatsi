import argparse

from hiru_tsatsi.presenters import start_report, terminal_offer_report
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.services import Services


def _tell(services: Services, summary: str, details: str) -> None:
    print(summary)
    print(details)
    services.notifier.notify(summary, details)


def report_and_offer(services: Services, outcome: Outcome) -> int:
    _tell(services, start_report.summary(outcome), start_report.details(outcome))
    offer = services.offer.run(outcome.stopped_without_window)
    if terminal_offer_report.anything_to_say(offer):
        _tell(services, terminal_offer_report.SUMMARY, terminal_offer_report.details(offer))
    return 0


def start(services: Services, chosen: argparse.Namespace) -> int:
    return report_and_offer(services, services.start.run())


def ask(services: Services, chosen: argparse.Namespace) -> int:
    outcome = services.ask.run()
    if outcome is None:
        return 0
    return report_and_offer(services, outcome)
