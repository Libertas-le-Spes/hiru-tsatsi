import unittest
from unittest.mock import create_autospec

from tests.examples.app_lists import app_list
from tests.examples.home import RECOGNISING
from tests.use_cases.starting_scene import HELPER, MAIN
from hiru_tsatsi.use_cases import app_starts
from hiru_tsatsi.use_cases.own_window_starts import MaybeTerminalStart, OwnWindowStart
from hiru_tsatsi.use_cases.ports import Desktop, Launched
from hiru_tsatsi.use_cases.terminal_starts import TerminalStart
from hiru_tsatsi.work_apps.app import App

KNOWN_HELPER = App("Helper", "cd code && helper", "hiru-tsatsi.2-0-helper", in_terminal=True)


class ChoosingHowToStartAnApp(unittest.TestCase):
    def kind_for(self, app: App):
        desktop = create_autospec(Desktop, instance=True)
        return type(app_starts.begin(desktop, app_list((2, [app])).placements()[0], 0.0, RECOGNISING))

    def test_an_app_known_to_need_a_terminal_starts_in_one(self):
        self.assertIs(self.kind_for(KNOWN_HELPER), TerminalStart)

    def test_a_folder_and_program_command_may_turn_out_to_need_one(self):
        self.assertIs(self.kind_for(HELPER), MaybeTerminalStart)

    def test_any_other_command_never_does(self):
        self.assertIs(self.kind_for(MAIN), OwnWindowStart)


class DecidingWhenAnAppNeedsATerminal(unittest.TestCase):
    def setUp(self):
        self.launched = create_autospec(Launched, instance=True)
        self.start = MaybeTerminalStart(app_list((2, [HELPER])).placements()[0], self.launched, since=100.0)

    def test_not_before_ten_seconds_even_if_it_stopped(self):
        self.launched.stopped.return_value = True
        self.assertFalse(self.start.needs_terminal(109.9))

    def test_after_ten_seconds_when_it_stopped(self):
        self.launched.stopped.return_value = True
        self.assertTrue(self.start.needs_terminal(110.0))

    def test_never_while_it_is_still_running(self):
        self.launched.stopped.return_value = False
        self.assertFalse(self.start.needs_terminal(500.0))


if __name__ == "__main__":
    unittest.main()
