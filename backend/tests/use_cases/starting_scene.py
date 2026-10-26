from unittest.mock import Mock, create_autospec

from tests.examples.clock import TickingClock
from tests.use_cases.mocked_list import store_holding
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.ports import WindowNames
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.windows import Window

CHAT = App("Chat", "omarchy-launch-webapp https://chat.google.com/", "chrome-chat.google.com")
MAIN = App("Rider Main", "rider ~/code/harbour", "harbour")
STEAM = App("Steam", "steam")


def appearing_once_launched(desktop: Mock, before: list[Window], after: list[Window]) -> None:
    def windows() -> list[Window]:
        if desktop.launch.called:
            return after
        return before
    desktop.windows.side_effect = windows


class Start:
    def __init__(self, desktop: Mock, apps: AppList):
        self.desktop = desktop
        self.store = store_holding(apps)
        self.names = create_autospec(WindowNames, instance=True)
        self.clock = TickingClock()

    def run(self) -> Outcome:
        return StartApps(self.desktop, self.store, self.names, self.clock, self.clock.wait).run()
