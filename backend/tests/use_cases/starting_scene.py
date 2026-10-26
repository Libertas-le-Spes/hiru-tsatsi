from unittest.mock import Mock, call, create_autospec

from tests.examples.clock import TickingClock
from tests.examples.home import RECOGNISING
from tests.use_cases.mocked_list import store_holding
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.ports import Announcer, Launch, Launches, Terminal, WindowNames
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.terminal_window import terminal_window_name
from hiru_tsatsi.work_apps.windows import Window

CHAT = App("Chat", "omarchy-launch-webapp https://chat.google.com/", "chrome-chat.google.com")
MAIN = App("Rider Main", "rider ~/code/harbour", "harbour")
STEAM = App("Steam", "steam")
HELPER = App("Helper", "cd code && helper")
HELPERS_TERMINAL = terminal_window_name(HELPER)


def watched(command: str) -> str:
    return f"[watched] {command}"


def in_a_terminal(command: str, window: str) -> str:
    return f"[terminal {window}] {command}"


def appearing_once_launched(desktop: Mock, before: list[Window], after: list[Window]) -> None:
    def windows() -> list[Window]:
        if desktop.launch.called:
            return after
        return before
    desktop.windows.side_effect = windows


class Start:
    def __init__(self, desktop: Mock, apps: AppList, stops: bool = False):
        self.desktop = desktop
        self.launch = create_autospec(Launch, instance=True)
        self.launch.wrapped.side_effect = watched
        self.launch.stopped.return_value = stops
        self.launches = create_autospec(Launches, instance=True)
        self.launches.new.return_value = self.launch
        self.terminal = create_autospec(Terminal, instance=True)
        self.terminal.command_for.side_effect = in_a_terminal
        self.store = store_holding(apps)
        self.names = create_autospec(WindowNames, instance=True)
        self.announcer = create_autospec(Announcer, instance=True)
        self.clock = TickingClock()

    def run(self) -> Outcome:
        launcher = Launcher(self.desktop, self.launches, self.terminal)
        return StartApps(self.desktop, launcher, self.store, self.names, self.clock, self.clock.wait,
                         self.announcer, RECOGNISING).run()

    def window_appearing_after(self, seconds: float, window: Window) -> None:
        def windows() -> list[Window]:
            if self.clock.now >= seconds:
                return [window]
            return []
        self.desktop.windows.side_effect = windows

    def window_appearing_in_its_terminal(self, window: Window) -> None:
        def windows() -> list[Window]:
            if self.opened_in_terminal():
                return [window]
            return []
        self.desktop.windows.side_effect = windows

    def opened_in_terminal(self) -> list:
        opened = []
        for launched in self.desktop.launch.call_args_list:
            if launched.args[0].startswith("[terminal"):
                opened.append(launched)
        return opened

    def opened_in_its_terminal(self, app: App, workspace: int) -> bool:
        return self.opened_in_terminal() == [call(in_a_terminal(app.command, terminal_window_name(app)), workspace)]
