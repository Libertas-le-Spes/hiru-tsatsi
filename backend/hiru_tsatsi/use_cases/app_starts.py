from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.own_window_starts import OwnWindowStart
from hiru_tsatsi.use_cases.start_shape import AppStart
from hiru_tsatsi.use_cases.terminal_starts import MaybeTerminalStart, TerminalStart
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising

FIRST_THAT_FITS = [TerminalStart, MaybeTerminalStart]


def begin(launcher: Launcher, placement: Placement, now: float, recognising: Recognising) -> AppStart:
    for kind in FIRST_THAT_FITS:
        if kind.fits(placement.app, recognising):
            return kind.begin(launcher, placement, now)
    return OwnWindowStart.begin(launcher, placement, now)
