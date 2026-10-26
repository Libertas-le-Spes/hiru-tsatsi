import argparse
import json

from hiru_tsatsi.presenters.bar_state import bar_state, window_choices
from hiru_tsatsi.use_cases.services import Services


def overview(services: Services, chosen: argparse.Namespace) -> int:
    print(json.dumps(bar_state(services.overview.run())))
    return 0


def windows_for(services: Services, chosen: argparse.Namespace) -> int:
    candidates = services.overview.candidates(chosen.workspace, chosen.index)
    print(json.dumps(window_choices(candidates)))
    return 0
