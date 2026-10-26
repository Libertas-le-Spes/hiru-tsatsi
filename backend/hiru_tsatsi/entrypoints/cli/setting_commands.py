import argparse

from hiru_tsatsi.presenters.outcome_text import set_up_text, window_titles_text
from hiru_tsatsi.use_cases.ports import ConfigLeftAlone, SetUpFailed
from hiru_tsatsi.wiring import App


def set_up(app: App, chosen: argparse.Namespace) -> int:
    return report_set_up(app)


def report_set_up(app: App) -> int:
    try:
        print(set_up_text(app.set_up.run()))
    except SetUpFailed as failed:
        print(f"The desktop reported a problem after setting up, so check its config:\n{failed}")
        return 1
    except ConfigLeftAlone as refused:
        print(f"Nothing was set up: {refused}.")
        return 1
    return 0


def window_titles(app: App, chosen: argparse.Namespace) -> int:
    if chosen.state:
        app.window_titles.turn(chosen.state == "on")
    print(window_titles_text(app.window_titles.wanted(), app.window_titles.chosen()))
    return 0
