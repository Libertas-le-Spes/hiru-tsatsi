from hiru_tsatsi.use_cases.app_start import AppStart
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.placing_windows import PlacingWindows
from hiru_tsatsi.use_cases.ports import Notifier
from hiru_tsatsi.use_cases.terminal_starts import TrialTerminalStart
from hiru_tsatsi.use_cases.watching_starts import WatchingStarts
from hiru_tsatsi.work_apps.placement import Placement

EXPLANATION = ("It stopped without opening a window. Some apps only run inside a terminal. "
               "Without a click it opens as it did, and you won't be asked again.")
ACTION = "Open in a terminal"


def _question(placement: Placement) -> str:
    return f"Open {placement.app.name} in a terminal?"


def _placements(starts: list[AppStart]) -> list[Placement]:
    placements = []
    for start in starts:
        placements.append(start.placement)
    return placements


class OfferingTerminals:
    def __init__(self, notifier: Notifier, launcher: Launcher, watching: WatchingStarts):
        self.notifier = notifier
        self.launcher = launcher
        self.watching = watching

    def offer(self, placing: PlacingWindows, confirming: ConfirmingTerminals,
              stopped: list[Placement]) -> list[Placement]:
        trials = []
        declined = []
        for placement in stopped:
            if self.notifier.ask(_question(placement), EXPLANATION, ACTION):
                trials.append(TrialTerminalStart.begin(self.launcher, placement))
            else:
                placing.rule_out_terminal(placement)
                declined.append(placement)
        unseen = self.watching.until_placed(placing, confirming, trials)
        self._rule_out_unconfirmed(placing, confirming, unseen)
        return declined + _placements(unseen)

    @staticmethod
    def _rule_out_unconfirmed(placing: PlacingWindows, confirming: ConfirmingTerminals,
                              unseen: list[AppStart]) -> None:
        for placement in confirming.unconfirmed():
            placing.rule_out_terminal(placement)
        for start in unseen:
            placing.rule_out_terminal(start.placement)
