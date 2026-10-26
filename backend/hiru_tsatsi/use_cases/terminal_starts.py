from dataclasses import dataclass
from typing import Protocol

from hiru_tsatsi.use_cases.ports import Desktop
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising


class Remembering(Protocol):
    def remember_terminal(self, placement: Placement) -> None: ...


@dataclass(frozen=True)
class TerminalStart:
    placement: Placement

    @staticmethod
    def fits(app: App, recognising: Recognising) -> bool:
        return app.in_terminal

    @classmethod
    def begin(cls, desktop: Desktop, placement: Placement, now: float) -> "TerminalStart":
        app = placement.app
        desktop.launch_in_terminal(app.command, placement.workspace, app.learned_window)
        return cls(placement)

    def needs_terminal(self, now: float) -> bool:
        return False

    def on_placed(self, remembering: Remembering) -> None:
        return None


@dataclass(frozen=True)
class TrialTerminalStart:
    placement: Placement

    @classmethod
    def begin(cls, desktop: Desktop, placement: Placement) -> "TrialTerminalStart":
        trial = placement.as_terminal()
        desktop.launch_in_terminal(trial.app.command, trial.workspace, trial.app.learned_window)
        return cls(trial)

    def needs_terminal(self, now: float) -> bool:
        return False

    def on_placed(self, remembering: Remembering) -> None:
        remembering.remember_terminal(self.placement)
