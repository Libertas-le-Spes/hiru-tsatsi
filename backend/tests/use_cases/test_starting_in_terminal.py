import unittest
from unittest.mock import create_autospec

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.starting_scene import (CHAT, HELPER, MAIN, Start, appearing_once_in_a_terminal,
                                            appearing_once_launched, launch_that, mocked_desktop)
from hiru_tsatsi.use_cases.app_starts import OwnWindowStart
from hiru_tsatsi.use_cases.ports import Launched
from hiru_tsatsi.work_apps.app import App

TERMINAL = "hiru-tsatsi.2-0-helper"
KNOWN_HELPER = App("Helper", "cd code && helper", TERMINAL, in_terminal=True)


def helper_that_stops(terminal_window_appears: bool) -> Start:
    desktop = mocked_desktop([])
    desktop.launch.return_value = launch_that(stopped=True)
    if terminal_window_appears:
        appearing_once_in_a_terminal(desktop, [window("t", TERMINAL, "foot", 2)])
    return Start(desktop, app_list((2, [HELPER])))


class StartingAppsThatNeedATerminal(unittest.TestCase):
    def test_a_command_that_stops_without_a_window_is_opened_again_in_a_terminal(self):
        start = helper_that_stops(terminal_window_appears=True)
        outcome = start.run()
        start.desktop.launch_in_terminal.assert_called_once_with("cd code && helper", 2, TERMINAL)
        self.assertEqual((outcome.in_terminal, outcome.unseen), (["Helper"], []))

    def test_remembers_that_the_app_opens_in_a_terminal(self):
        start = helper_that_stops(terminal_window_appears=True)
        start.run()
        remembered = start.saved().placements()[0].app
        self.assertEqual((remembered.in_terminal, remembered.learned_window), (True, TERMINAL))

    def test_an_app_known_to_need_a_terminal_opens_in_one_at_once(self):
        desktop = mocked_desktop([])
        appearing_once_in_a_terminal(desktop, [window("t", TERMINAL, "foot", 2)])
        start = Start(desktop, app_list((2, [KNOWN_HELPER])))
        outcome = start.run()
        desktop.launch.assert_not_called()
        desktop.launch_in_terminal.assert_called_once_with("cd code && helper", 2, TERMINAL)
        self.assertEqual((outcome.unseen, start.clock.now), ([], 0.5))

    def test_a_slow_app_still_running_is_never_put_in_a_terminal(self):
        start = Start(mocked_desktop([]), app_list((2, [MAIN])))
        outcome = start.run()
        start.desktop.launch_in_terminal.assert_not_called()
        self.assertEqual(outcome.unseen, ["Rider Main"])

    def test_a_command_that_hands_its_window_to_a_running_app_is_not_put_in_a_terminal(self):
        desktop = mocked_desktop([])
        desktop.launch.return_value = launch_that(stopped=True)
        appearing_once_launched(desktop, [], [window("c", "chrome-chat.google.com-Default", "Chat", 1)])
        outcome = Start(desktop, app_list((1, [CHAT]))).run()
        desktop.launch_in_terminal.assert_not_called()
        self.assertEqual((outcome.started, outcome.unseen), (["Chat"], []))

    def test_a_session_opened_by_hand_in_the_right_folder_counts_as_open_and_is_moved(self):
        by_hand = window("h", "foot", "✳ Some talk", 4, "helper", "/home/sam/code")
        desktop = mocked_desktop([by_hand])
        start = Start(desktop, app_list((2, [HELPER])))
        outcome = start.run()
        desktop.launch.assert_not_called()
        desktop.launch_in_terminal.assert_not_called()
        desktop.move.assert_called_once_with(by_hand, 2)
        start.store.save.assert_not_called()
        self.assertEqual(outcome.already_open, ["Helper"])

    def test_a_terminal_app_finds_its_session_opened_by_hand(self):
        desktop = mocked_desktop([window("h", "foot", "✳ Some talk", 2, "helper", "/home/sam/code")])
        outcome = Start(desktop, app_list((2, [KNOWN_HELPER]))).run()
        desktop.launch_in_terminal.assert_not_called()
        self.assertEqual(outcome.already_open, ["Helper"])


class DecidingWhenAnAppNeedsATerminal(unittest.TestCase):
    def setUp(self):
        self.launched = create_autospec(Launched, instance=True)
        self.start = OwnWindowStart(app_list((2, [HELPER])).placements()[0], self.launched, since=100.0)

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
