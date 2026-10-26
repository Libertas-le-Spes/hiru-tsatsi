import unittest
from unittest.mock import create_autospec

from tests.examples.app_lists import app_list
from tests.examples.home import RECOGNISING
from tests.use_cases.starting_scene import HELPER, MAIN
from hiru_tsatsi.use_cases import app_starts
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.own_window_starts import OwnWindowStart
from hiru_tsatsi.use_cases.ports import Launch
from hiru_tsatsi.use_cases.terminal_starts import MaybeTerminalStart, TerminalStart, TrialTerminalStart
from hiru_tsatsi.work_apps.app import App

KNOWN_HELPER = App("Helper", "cd code && helper", "hiru-tsatsi.helper-1a2b3c4d", in_terminal=True)


def kind_for(app: App) -> type:
    launcher = create_autospec(Launcher, instance=True)
    return type(app_starts.begin(launcher, app_list((2, [app])).placements()[0], 0.0, RECOGNISING))


class ChoosingHowToStartAnApp(unittest.TestCase):
    def test_an_app_known_to_need_a_terminal_starts_in_one(self):
        self.assertIs(kind_for(KNOWN_HELPER), TerminalStart)

    def test_a_folder_and_program_command_may_turn_out_to_need_one(self):
        self.assertIs(kind_for(HELPER), MaybeTerminalStart)

    def test_any_other_command_starts_with_its_own_window(self):
        self.assertIs(kind_for(MAIN), OwnWindowStart)


class DecidingWhenAnAppNeedsATerminal(unittest.TestCase):
    def setUp(self):
        self.launch = create_autospec(Launch, instance=True)
        self.launcher = create_autospec(Launcher, instance=True)
        placement = app_list((2, [HELPER])).placements()[0]
        self.start = MaybeTerminalStart(placement, self.launch, 100.0, self.launcher)

    def test_not_before_ten_seconds_even_if_it_stopped(self):
        self.launch.stopped.return_value = True
        self.assertIs(self.start.next(109.9), self.start)
        self.launcher.in_terminal.assert_not_called()

    def test_after_ten_seconds_when_it_stopped_it_tries_a_terminal_once(self):
        self.launch.stopped.return_value = True
        self.assertIsInstance(self.start.next(110.0), TrialTerminalStart)
        self.launcher.in_terminal.assert_called_once()

    def test_never_while_it_is_still_running(self):
        self.launch.stopped.return_value = False
        self.assertIs(self.start.next(500.0), self.start)
        self.launcher.in_terminal.assert_not_called()


if __name__ == "__main__":
    unittest.main()
