from dataclasses import dataclass

from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.ports import Launch
from hiru_tsatsi.use_cases.start_shape import AppStart, Remembering
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.terminal_window import in_a_terminal

TERMINAL_AFTER_SECONDS = 10.0


@dataclass(frozen=True)
class TerminalStart:
    placement: Placement

    @staticmethod
    def fits(app: App, recognising: Recognising) -> bool:
        return app.in_terminal

    @classmethod
    def begin(cls, launcher: Launcher, placement: Placement, now: float) -> "TerminalStart":
        launcher.in_terminal(placement)
        return cls(placement)

    def next(self, now: float) -> AppStart:
        return self

    def on_placed(self, remembering: Remembering) -> None:
        return None


@dataclass(frozen=True)
class TrialTerminalStart:
    placement: Placement

    @classmethod
    def begin(cls, launcher: Launcher, placement: Placement) -> "TrialTerminalStart":
        trial = Placement(placement.workspace, placement.index, in_a_terminal(placement.app))
        launcher.in_terminal(trial)
        return cls(trial)

    def next(self, now: float) -> AppStart:
        return self

    def on_placed(self, remembering: Remembering) -> None:
        remembering.remember_terminal(self.placement)


@dataclass(frozen=True)
class MaybeTerminalStart:
    placement: Placement
    launch: Launch
    since: float
    launcher: Launcher

    @staticmethod
    def fits(app: App, recognising: Recognising) -> bool:
        return recognising.recognised_by_what_runs(app)

    @classmethod
    def begin(cls, launcher: Launcher, placement: Placement, now: float) -> "MaybeTerminalStart":
        return cls(placement, launcher.watched(placement), now, launcher)

    def next(self, now: float) -> AppStart:
        if not self.needs_terminal(now):
            return self
        return TrialTerminalStart.begin(self.launcher, self.placement)

    def needs_terminal(self, now: float) -> bool:
        waited_long_enough = now - self.since >= TERMINAL_AFTER_SECONDS
        return waited_long_enough and self.launch.stopped()

    def on_placed(self, remembering: Remembering) -> None:
        return None
