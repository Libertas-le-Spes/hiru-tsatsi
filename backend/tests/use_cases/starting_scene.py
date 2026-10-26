from unittest.mock import Mock, create_autospec

from tests.examples.clock import TickingClock
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.ports import AppListStore, Desktop, WindowNames
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.windows import Window

CHAT = App("Chat", "omarchy-launch-webapp https://chat.google.com/", "chrome-chat.google.com")
MAIN = App("Rider Main", "rider ~/code/harbour", "harbour")
STEAM = App("Steam", "steam")


def mocked_desktop(open_now: list[Window]) -> Mock:
    desktop = create_autospec(Desktop, instance=True)
    desktop.windows.return_value = open_now
    return desktop


def appearing_once_launched(desktop: Mock, before: list[Window], after: list[Window]) -> None:
    def windows() -> list[Window]:
        if desktop.launch.called:
            return after
        return before
    desktop.windows.side_effect = windows


class Start:
    def __init__(self, desktop: Mock, apps: AppList):
        self.desktop = desktop
        self.store = create_autospec(AppListStore, instance=True)
        self.store.load.return_value = apps
        self.names = create_autospec(WindowNames, instance=True)
        self.clock = TickingClock()

    def run(self) -> Outcome:
        return StartApps(self.desktop, self.store, self.names, self.clock, self.clock.wait).run()

    def saved(self) -> AppList:
        self.store.save.assert_called_once()
        return self.store.save.call_args.args[0]
