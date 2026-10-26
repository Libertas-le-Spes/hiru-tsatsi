from dataclasses import dataclass

from hiru_tsatsi.use_cases.app_start import AppStart, placements_of
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals, Trial
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.learned_apps import LearnedApps
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Clock, Desktop, WindowNames
from hiru_tsatsi.use_cases.terminal_starts import TerminalStart
from hiru_tsatsi.use_cases.watching_starts import WatchingStarts
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.terminal_window import as_terminal_app
from hiru_tsatsi.work_apps.windows import addresses_of


@dataclass(frozen=True)
class Tried:
    apps: AppList
    confirmed: list[Placement]
    not_confirmed: list[Placement]


def _in_a_trial_terminal(placement: Placement) -> Placement:
    return Placement(placement.workspace, placement.index, as_terminal_app(placement.app))


class TryingTerminals:
    def __init__(self, desktop: Desktop, names: WindowNames, launcher: Launcher, recognising: Recognising,
                 watching: WatchingStarts, confirming: ConfirmingTerminals, clock: Clock):
        self.desktop = desktop
        self.names = names
        self.launcher = launcher
        self.recognising = recognising
        self.watching = watching
        self.confirming = confirming
        self.clock = clock

    def try_out(self, apps: AppList, placements: list[Placement]) -> Tried:
        learned = LearnedApps(apps)
        placing = PlacingWindows(self.desktop, self.names, learned, addresses_of(self.desktop.windows()),
                                 self.recognising)
        trials = self._begin_all(placements)
        unseen = placements_of(self.watching.until_placed(placing, trials))
        confirmed = self.confirming.confirmed_among(self._seen(placing, trials, unseen))
        not_confirmed = self._settled(learned, placements_of(trials), confirmed)
        return Tried(learned.apps, confirmed, not_confirmed)

    def _begin_all(self, placements: list[Placement]) -> list[AppStart]:
        trials = []
        for placement in placements:
            trials.append(TerminalStart.begin(self.launcher, _in_a_trial_terminal(placement), self.clock.now()))
        return trials

    @staticmethod
    def _seen(placing: PlacingWindows, trials: list[AppStart], unseen: list[Placement]) -> list[Trial]:
        seen = []
        for trial in trials:
            if trial.placement not in unseen:
                seen.append((trial.placement, placing.window_given_to(trial.placement)))
        return seen

    @staticmethod
    def _settled(learned: LearnedApps, tried: list[Placement], confirmed: list[Placement]) -> list[Placement]:
        not_confirmed = []
        for placement in tried:
            if placement in confirmed:
                learned.remember_terminal(placement)
            else:
                learned.rule_out_terminal(placement)
                not_confirmed.append(placement)
        return not_confirmed
