import argparse

from hiru_tsatsi.entrypoints.set_up_report import report_set_up
from hiru_tsatsi.presenters.outcome_text import window_titles_text
from hiru_tsatsi.wiring import Services


def set_up(services: Services, chosen: argparse.Namespace) -> int:
    return report_set_up(services)


def window_titles(services: Services, chosen: argparse.Namespace) -> int:
    if chosen.state:
        services.window_titles.turn(chosen.state == "on")
    print(window_titles_text(services.window_titles.wanted(), services.window_titles.chosen()))
    return 0
