import argparse
from typing import Callable

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


def _outcome_of(services: Services, starting: Callable[[], Outcome | None]) -> Outcome | None:
    try:
        return starting()
    except StartRefused as refused:
        services.notifier.notify(NOT_STARTED, refused.explained())
        raise


def start(services: Services, chosen: argparse.Namespace) -> int:
    return _report_and_offer(services, _outcome_of(services, services.start.run))


def ask(services: Services, chosen: argparse.Namespace) -> int:
    outcome = _outcome_of(services, services.ask.run)
    if outcome is None:
        return 0
    return _report_and_offer(services, outcome)
