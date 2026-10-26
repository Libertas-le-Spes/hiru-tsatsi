from hiru_tsatsi.use_cases.own_window_starts import MaybeTerminalStart, OwnWindowStart
from hiru_tsatsi.use_cases.ports import Desktop
from hiru_tsatsi.use_cases.terminal_starts import TerminalStart, TrialTerminalStart
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising

AppStart = TerminalStart | TrialTerminalStart | MaybeTerminalStart | OwnWindowStart
FIRST_THAT_FITS = [TerminalStart, MaybeTerminalStart, OwnWindowStart]


def begin(desktop: Desktop, placement: Placement, now: float, recognising: Recognising) -> AppStart:
    for kind in FIRST_THAT_FITS:
        if kind.fits(placement.app, recognising):
            return kind.begin(desktop, placement, now)
    raise LookupError(placement.app.name)
