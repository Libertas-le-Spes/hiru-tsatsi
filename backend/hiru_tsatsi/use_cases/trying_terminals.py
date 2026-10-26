from dataclasses import dataclass

from hiru_tsatsi.use_cases.app_start import AppStart, placements_of
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Clock, Desktop, WindowNames
from hiru_tsatsi.use_cases.terminal_starts import TrialTerminalStart
from hiru_tsatsi.use_cases.watching_starts import WatchingStarts
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.windows import addresses_of


@dataclass(frozen=True)
class Tried:
    apps: AppList
    confirmed: list[Placement]
    not_confirmed: list[Placement]


class TryingTerminals:
    def __init__(self, desktop: Desktop, names: WindowNames, launcher: Launcher, recognising: Recognising,
                 watching: WatchingStarts, clock: Clock):
        self.desktop = desktop
        self.names = names
        self.launcher = launcher
        self.recognising = recognising
        self.watching = watching
        self.clock = clock

    def try_out(self, apps: AppList, placements: list[Placement]) -> Tried:
        placing = PlacingWindows(self.desktop, self.names, apps, addresses_of(self.desktop.windows()), self.recognising)
        confirming = ConfirmingTerminals(self.recognising)
        unseen = self.watching.until_placed(placing, confirming, self._begin_all(placements))
        not_confirmed = confirming.unconfirmed() + placements_of(unseen)
        for placement in not_confirmed:
            placing.rule_out_terminal(placement)
        return Tried(placing.apps, confirming.confirmed, not_confirmed)

    def _begin_all(self, placements: list[Placement]) -> list[AppStart]:
        trials = []
        for placement in placements:
            trials.append(TrialTerminalStart.begin(self.launcher, placement, self.clock.now()))
        return trials
