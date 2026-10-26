from dataclasses import dataclass, field

from hiru_tsatsi.use_cases.learned_during_start import save_learned, still_the_same_app
from hiru_tsatsi.use_cases.ports import AppListStore, Notifier
from hiru_tsatsi.use_cases.trying_terminals import TryingTerminals
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.placement import Placement

QUESTION_SECONDS = 60.0
EXPLANATION = ("It stopped without opening a window. Some apps only run inside a terminal. "
               "Without a click within a minute it is left as it is, and you won't be asked again.")
ACTION = "Open in a terminal"


def _question(placement: Placement) -> str:
    return f"Open {placement.app.name} in a terminal?"


def _names(placements: list[Placement]) -> list[str]:
    names = []
    for placement in placements:
        names.append(placement.app.name)
    return names


def _with_terminal_ruled_out(apps: AppList, placements: list[Placement]) -> AppList:
    for placement in placements:
        apps = apps.with_terminal_ruled_out(placement)
    return apps


@dataclass(frozen=True)
class TerminalOffer:
    now_opens_in_terminal: list[str] = field(default_factory=list)
    not_offered_again: list[str] = field(default_factory=list)


class OfferTerminals:
    def __init__(self, notifier: Notifier, store: AppListStore, trying: TryingTerminals):
        self.notifier = notifier
        self.store = store
        self.trying = trying

    def run(self, stopped: list[Placement]) -> TerminalOffer:
        if not stopped:
            return TerminalOffer()
        apps = self.store.load()
        wanted, declined = self._answers(self._still_there(apps, stopped))
        tried = self.trying.try_out(_with_terminal_ruled_out(apps, declined), wanted)
        save_learned(self.store, apps, tried.apps)
        return TerminalOffer(now_opens_in_terminal=_names(tried.confirmed),
                             not_offered_again=_names(declined + tried.not_confirmed))

    @staticmethod
    def _still_there(apps: AppList, stopped: list[Placement]) -> list[Placement]:
        there = []
        for placement in stopped:
            if still_the_same_app(apps, placement):
                there.append(placement)
        return there

    def _answers(self, placements: list[Placement]) -> tuple[list[Placement], list[Placement]]:
        wanted = []
        declined = []
        for placement in placements:
            if self.notifier.ask_within(_question(placement), EXPLANATION, ACTION, QUESTION_SECONDS):
                wanted.append(placement)
            else:
                declined.append(placement)
        return wanted, declined
