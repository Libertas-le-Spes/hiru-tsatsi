from dataclasses import dataclass

from hiru_tsatsi.use_cases.ports import Desktop, Launched
from hiru_tsatsi.use_cases.terminal_starts import Remembering
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising

TERMINAL_AFTER_SECONDS = 10.0


@dataclass(frozen=True)
class MaybeTerminalStart:
    placement: Placement
    launched: Launched
    since: float

    @staticmethod
    def fits(app: App, recognising: Recognising) -> bool:
        return recognising.by_what_runs(app)

    @classmethod
    def begin(cls, desktop: Desktop, placement: Placement, now: float) -> "MaybeTerminalStart":
        launched = desktop.launch(placement.app.command, placement.workspace)
        return cls(placement, launched, now)

    def needs_terminal(self, now: float) -> bool:
        waited_long_enough = now - self.since >= TERMINAL_AFTER_SECONDS
        return waited_long_enough and self.launched.stopped()

    def on_placed(self, remembering: Remembering) -> None:
        return None


@dataclass(frozen=True)
class OwnWindowStart:
    placement: Placement

    @staticmethod
    def fits(app: App, recognising: Recognising) -> bool:
        return True

    @classmethod
    def begin(cls, desktop: Desktop, placement: Placement, now: float) -> "OwnWindowStart":
        desktop.launch(placement.app.command, placement.workspace)
        return cls(placement)

    def needs_terminal(self, now: float) -> bool:
        return False

    def on_placed(self, remembering: Remembering) -> None:
        return None
