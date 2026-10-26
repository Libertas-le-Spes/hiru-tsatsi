from unittest.mock import Mock, call, create_autospec

from tests.examples.clock import TickingClock
from tests.examples.home import RECOGNISING
from tests.use_cases.mocked_list import store_holding
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.offering_terminals import OfferTerminals, TerminalOffer
from hiru_tsatsi.use_cases.ports import Announcer, Launch, Launches, Notifier, OneStartAtATime, Terminal, WindowNames
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.use_cases.trying_terminals import TryingTerminals
from hiru_tsatsi.use_cases.watching_starts import WATCH_SECONDS, WatchingStarts
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
    def __init__(self, desktop: Mock, apps: AppList, stops: bool = False, answers_yes: bool = False):
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
        self.notifier = create_autospec(Notifier, instance=True)
        self.notifier.ask_within.return_value = answers_yes
        self.one_at_a_time = create_autospec(OneStartAtATime, instance=True)
        self.one_at_a_time.claimed.return_value = True
        self.clock = TickingClock()
        self.launcher = Launcher(self.desktop, self.launches, self.terminal)
        self.watching = WatchingStarts(self.desktop, self.clock, WATCH_SECONDS)

    def run(self) -> Outcome:
        return StartApps(self.desktop, self.launcher, self.store, self.names, self.announcer, RECOGNISING,
                         self.watching, self.clock, self.one_at_a_time).run()

    def run_and_offer(self) -> tuple[Outcome, TerminalOffer]:
        outcome = self.run()
        trying = TryingTerminals(self.desktop, self.names, self.launcher, RECOGNISING, self.watching, self.clock)
        return outcome, OfferTerminals(self.notifier, self.store, trying).run(outcome.stopped_without_window)

    def window_appearing_after(self, seconds: float, window: Window) -> None:
        def windows() -> list[Window]:
            if self.clock.seconds >= seconds:
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
