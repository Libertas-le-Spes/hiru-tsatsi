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
    offer = services.offer.run(outcome.stopped_without_window)
    if terminal_offer_report.anything_to_say(offer):
        _tell(services, terminal_offer_report.SUMMARY, terminal_offer_report.details(offer))
    return 0


def start(services: Services, chosen: argparse.Namespace) -> int:
    try:
        return _report_and_offer(services, services.start.run())
    except StartRefused as refused:
        services.notifier.notify(NOT_STARTED, refused.explained())
        raise


def ask(services: Services, chosen: argparse.Namespace) -> int:
    try:
        outcome = services.ask.run()
        if outcome is None:
            return 0
        return _report_and_offer(services, outcome)
    except StartRefused as refused:
        services.notifier.notify(NOT_STARTED, refused.explained())
        raise
