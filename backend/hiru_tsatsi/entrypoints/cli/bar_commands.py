import argparse
import json
import sys

from hiru_tsatsi.presenters.bar_state import bar_state, window_choices
from hiru_tsatsi.wiring import App
from hiru_tsatsi.work_apps.refusals import Refused


def overview(app: App, chosen: argparse.Namespace) -> int:
    print(json.dumps(bar_state(app.overview.run(), app.window_titles.wanted())))
    return 0


def windows_for(app: App, chosen: argparse.Namespace) -> int:
    try:
        candidates = app.overview.candidates(chosen.workspace, chosen.index)
    except Refused as refused:
        print(refused, file=sys.stderr)
        return 1
    print(json.dumps(window_choices(candidates)))
    return 0
