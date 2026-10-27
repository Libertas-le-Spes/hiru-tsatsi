from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.placement import Placement


class LearnedApps:
    def __init__(self, apps: AppList):
        self.apps = apps

    def learn_window(self, placement: Placement, window: str) -> None:
        self.apps = self.apps.with_learned_window(placement, window)

    def remember_terminal(self, placement: Placement) -> None:
        self.apps = self.apps.with_terminal(placement)

    def rule_out_terminal(self, placement: Placement) -> None:
        self.apps = self.apps.with_terminal_ruled_out(placement)
