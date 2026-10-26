from dataclasses import dataclass

from hiru_tsatsi.use_cases.ports import Desktop, Launched
from hiru_tsatsi.work_apps.placement import Placement

TERMINAL_AFTER_SECONDS = 10.0


@dataclass(frozen=True)
class OwnWindowStart:
    placement: Placement
    launched: Launched
    since: float

    @classmethod
    def begin(cls, desktop: Desktop, placement: Placement, now: float) -> "OwnWindowStart":
        launched = desktop.launch(placement.app.command, placement.workspace)
        return cls(placement, launched, now)

    def needs_terminal(self, now: float) -> bool:
        waited_long_enough = now - self.since >= TERMINAL_AFTER_SECONDS
        return waited_long_enough and self.launched.stopped()


@dataclass(frozen=True)
class TerminalStart:
    placement: Placement

    @classmethod
    def begin(cls, desktop: Desktop, placement: Placement) -> "TerminalStart":
        app = placement.app
        desktop.launch_in_terminal(app.command, placement.workspace, app.learned_window)
        return cls(placement)

    def needs_terminal(self, now: float) -> bool:
        return False


AppStart = OwnWindowStart | TerminalStart


def begin(desktop: Desktop, placement: Placement, now: float) -> AppStart:
    if placement.app.in_terminal:
        return TerminalStart.begin(desktop, placement)
    return OwnWindowStart.begin(desktop, placement, now)
