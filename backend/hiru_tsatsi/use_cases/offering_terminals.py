from dataclasses import dataclass, field

from hiru_tsatsi.use_cases.failures import AlreadyStarting
from hiru_tsatsi.use_cases.learned_during_start import save_learned, still_the_same_app
from hiru_tsatsi.use_cases.ports import AppListStore, Notifier, OneStartAtATime
from hiru_tsatsi.use_cases.trying_terminals import TryingTerminals
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.placement import Placement, names_of

QUESTION_SECONDS = 60.0
EXPLANATION = ("It stopped without opening a window. Some apps only run inside a terminal. "
               "Without a click within a minute it is left as it is, and you won't be asked again.")
ACTION = "Open in a terminal"


def _question(placement: Placement) -> str:
    return f"Open {placement.app.name} in a terminal?"


def _still_there(apps: AppList, placements: list[Placement]) -> list[Placement]:
    there = []
    for placement in placements:
        if still_the_same_app(apps, placement):
            there.append(placement)
    return there


def _with_terminal_ruled_out(apps: AppList, placements: list[Placement]) -> AppList:
    for placement in placements:
        apps = apps.with_terminal_ruled_out(placement)
    return apps


@dataclass(frozen=True)
class Answers:
    wanted: list[Placement] = field(default_factory=list)
    declined: list[Placement] = field(default_factory=list)


@dataclass(frozen=True)
class TerminalOffer:
    now_opens_in_terminal: list[str] = field(default_factory=list)
    not_offered_again: list[str] = field(default_factory=list)


class OfferTerminals:
    def __init__(self, notifier: Notifier, store: AppListStore, trying: TryingTerminals,
                 one_at_a_time: OneStartAtATime):
        self.notifier = notifier
        self.store = store
        self.trying = trying
        self.one_at_a_time = one_at_a_time

    def run(self, stopped: list[Placement]) -> TerminalOffer:
        if not stopped:
            return TerminalOffer()
        if not self.one_at_a_time.claimed():
            raise AlreadyStarting()
        to_ask = _still_there(self.store.load(), stopped)
        answers = self._answers(to_ask)
        apps = self.store.load()
        wanted = _still_there(apps, answers.wanted)
        declined = _still_there(apps, answers.declined)
        tried = self.trying.try_out(_with_terminal_ruled_out(apps, declined), wanted)
        save_learned(self.store, apps, tried.apps)
        not_offered_again = declined + tried.not_confirmed
        return TerminalOffer(now_opens_in_terminal=names_of(tried.confirmed),
                             not_offered_again=names_of(not_offered_again))

    def _answers(self, placements: list[Placement]) -> "Answers":
        answers = Answers()
        for placement in placements:
            answer = self.notifier.ask_within(_question(placement), EXPLANATION, ACTION, QUESTION_SECONDS)
            if answer is True:
                answers.wanted.append(placement)
            if answer is False:
                answers.declined.append(placement)
        return answers
