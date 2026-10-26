from dataclasses import dataclass, field

from hiru_tsatsi.use_cases.failures import AlreadyStarting
from hiru_tsatsi.use_cases.handover import Handover
from hiru_tsatsi.use_cases.late_windows import LateWindows
from hiru_tsatsi.use_cases.learned_during_start import save_learned, still_the_same_app
from hiru_tsatsi.use_cases.ports import Answer, AppListStore, Notifier, OneStartAtATime
from hiru_tsatsi.use_cases.trying_terminals import TryingTerminals
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.placement import Placement, names_of

QUESTION_SECONDS = 60.0
EXPLANATION = ("It stopped without opening a window. Some apps only run inside a terminal. "
               "Close this to never be asked again; leave it, and you'll be asked next time.")
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
class TerminalOffer:
    now_opens_in_terminal: list[str] = field(default_factory=list)
    not_offered_again: list[str] = field(default_factory=list)
    window_found_after_all: list[str] = field(default_factory=list)


class OfferTerminals:
    def __init__(self, notifier: Notifier, store: AppListStore, late: LateWindows, trying: TryingTerminals,
                 one_at_a_time: OneStartAtATime):
        self.notifier = notifier
        self.store = store
        self.late = late
        self.trying = trying
        self.one_at_a_time = one_at_a_time

    def run(self, handover: Handover) -> TerminalOffer:
        if not handover.stopped:
            return TerminalOffer()
        if not self.one_at_a_time.claimed():
            raise AlreadyStarting()
        found_late = []
        taken = set(handover.taken)
        answers = {Answer.YES: [], Answer.NO: [], Answer.NOT_ANSWERED: []}
        for placement in _still_there(self.store.load(), handover.stopped):
            late_window = self.late.placed(placement, handover.known_before, taken)
            if late_window is None:
                answers[self._asked(placement)].append(placement)
            else:
                taken.add(late_window.address)
                found_late.append(placement)
        return self._settled(answers[Answer.YES], answers[Answer.NO], found_late)

    def _asked(self, placement: Placement) -> Answer:
        return self.notifier.ask_within(_question(placement), EXPLANATION, ACTION, QUESTION_SECONDS)

    def _settled(self, said_yes: list[Placement], said_no: list[Placement],
                 found_late: list[Placement]) -> TerminalOffer:
        apps = self.store.load()
        wanted = _still_there(apps, said_yes)
        declined = _still_there(apps, said_no)
        tried = self.trying.try_out(_with_terminal_ruled_out(apps, declined), wanted)
        save_learned(self.store, apps, tried.apps)
        not_offered_again = declined + tried.not_confirmed
        return TerminalOffer(now_opens_in_terminal=names_of(tried.confirmed),
                             not_offered_again=names_of(not_offered_again),
                             window_found_after_all=names_of(found_late))
