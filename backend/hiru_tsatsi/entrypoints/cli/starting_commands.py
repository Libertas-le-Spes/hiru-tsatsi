import argparse

from hiru_tsatsi.presenters import start_report, terminal_offer_report
from hiru_tsatsi.use_cases.failures import StartRefused
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.services import Services

NOT_STARTED = "Work apps not started"


def _tell(services: Services, summary: str, details: str) -> None:
    print(summary)
    print(details)
    services.notifier.notify(summary, details)


def _report_and_offer(services: Services, outcome: Outcome) -> int:
    _tell(services, start_report.summary(outcome), start_report.details(outcome))
    offer = services.offer.run(outcome.for_the_offer)
    if terminal_offer_report.anything_to_say(offer):
        _tell(services, terminal_offer_report.SUMMARY, terminal_offer_report.details(offer))
    return 0


def _refused_on_screen(services: Services, refused: StartRefused) -> None:
    services.notifier.notify(NOT_STARTED, refused.explained())


def start(services: Services, chosen: argparse.Namespace) -> int:
    try:
        outcome = services.start.run()
    except StartRefused as refused:
        _refused_on_screen(services, refused)
        raise
    return _report_and_offer(services, outcome)


def ask(services: Services, chosen: argparse.Namespace) -> int:
    try:
        outcome = services.ask.run()
    except StartRefused as refused:
        _refused_on_screen(services, refused)
        raise
    if outcome is None:
        return 0
    return _report_and_offer(services, outcome)
