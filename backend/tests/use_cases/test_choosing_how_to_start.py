import unittest
from unittest.mock import create_autospec

from tests.examples.app_lists import app_list
from tests.examples.home import RECOGNISING
from tests.use_cases.starting_scene import HELPER, MAIN
from hiru_tsatsi.use_cases import choosing_how_to_start
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.own_window_starts import OwnWindowStart
from hiru_tsatsi.use_cases.ports import Launch
from hiru_tsatsi.use_cases.terminal_starts import TerminalStart
from hiru_tsatsi.use_cases.watched_starts import StoppedWithoutWindow, WatchedStart
from hiru_tsatsi.work_apps.app import App

KNOWN_HELPER = App("Helper", "cd code && helper", "hiru-tsatsi.helper-1a2b3c4d", opens_in_terminal=True)


def kind_for(app: App) -> type:
    launcher = create_autospec(Launcher, instance=True)
    return type(choosing_how_to_start.begin(launcher, app_list((2, [app])).placements()[0], 0.0, RECOGNISING))


class ChoosingHowToStartAnApp(unittest.TestCase):
    def test_an_app_known_to_need_a_terminal_starts_in_one(self):
        self.assertIs(kind_for(KNOWN_HELPER), TerminalStart)

    def test_a_folder_and_program_command_may_turn_out_to_need_one(self):
        self.assertIs(kind_for(HELPER), WatchedStart)

    def test_a_folder_and_program_command_whose_terminal_was_ruled_out_starts_with_its_own_window(self):
        self.assertIs(kind_for(App("Helper", "cd code && helper", terminal_ruled_out=True)), OwnWindowStart)

    def test_an_app_known_to_need_a_terminal_is_never_also_watched(self):
        self.assertFalse(WatchedStart.fits(KNOWN_HELPER, RECOGNISING))

    def test_any_other_command_starts_with_its_own_window(self):
        self.assertIs(kind_for(MAIN), OwnWindowStart)


class DecidingWhenAWatchedLaunchStoppedWithoutAWindow(unittest.TestCase):
    def setUp(self):
        self.launch = create_autospec(Launch, instance=True)
        self.placement = app_list((2, [HELPER])).placements()[0]
        self.start = WatchedStart(self.placement, self.launch, 100.0)

    def test_not_before_ten_seconds_even_if_it_stopped(self):
        self.launch.stopped.return_value = True
        self.assertIs(self.start.next(109.9), self.start)

    def test_after_ten_seconds_when_it_stopped(self):
        self.launch.stopped.return_value = True
        self.assertEqual(self.start.next(110.0), StoppedWithoutWindow(self.placement))

    def test_never_while_it_is_still_running(self):
        self.launch.stopped.return_value = False
        self.assertIs(self.start.next(500.0), self.start)


if __name__ == "__main__":
    unittest.main()
