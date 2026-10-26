from hiru_tsatsi.use_cases.app_start import AppStart
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.own_window_starts import OwnWindowStart
from hiru_tsatsi.use_cases.terminal_starts import TerminalStart
from hiru_tsatsi.use_cases.watched_starts import WatchedStart
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising

TERMINAL_KINDS = [TerminalStart, WatchedStart]


def begin(launcher: Launcher, placement: Placement, now: float, recognising: Recognising) -> AppStart:
    for kind in TERMINAL_KINDS:
        if kind.fits(placement.app, recognising):
            return kind.begin(launcher, placement, now)
    return OwnWindowStart.begin(launcher, placement, now)
