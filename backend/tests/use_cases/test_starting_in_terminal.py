import unittest

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.starting_scene import (CHAT, HELPER, Start, appearing_once_in_a_terminal, appearing_once_launched,
                                            launch_that, mocked_desktop)
from hiru_tsatsi.work_apps.app import App

TERMINAL = "hiru-tsatsi.2-0-helper"
KNOWN_HELPER = App("Helper", "cd code && helper", TERMINAL, in_terminal=True)
TYPO = App("Typo", "chromiun --app=https://example.org/")


def helper_that_stops() -> Start:
    desktop = mocked_desktop([])
    desktop.launch.return_value = launch_that(stopped=True)
    return Start(desktop, app_list((2, [HELPER])))


class StartingAppsThatNeedATerminal(unittest.TestCase):
    def test_a_folder_and_program_command_that_stops_without_a_window_is_opened_in_a_terminal(self):
        start = helper_that_stops()
        appearing_once_in_a_terminal(start.desktop, [window("t", TERMINAL, "foot", 2)])
        outcome = start.run()
        start.desktop.launch_in_terminal.assert_called_once_with("cd code && helper", 2, TERMINAL)
        self.assertEqual((outcome.in_terminal, outcome.unseen), (["Helper"], []))

    def test_needing_a_terminal_is_saved_once_its_window_is_found(self):
        start = helper_that_stops()
        appearing_once_in_a_terminal(start.desktop, [window("t", TERMINAL, "foot", 2)])
        start.run()
        remembered = start.saved().placements()[0].app
        self.assertEqual((remembered.in_terminal, remembered.learned_window), (True, TERMINAL))

    def test_nothing_is_saved_when_the_terminal_window_never_appears(self):
        start = helper_that_stops()
        outcome = start.run()
        start.desktop.launch_in_terminal.assert_called_once()
        start.store.save.assert_not_called()
        self.assertEqual((outcome.in_terminal, outcome.unseen), ([], ["Helper"]))

    def test_a_launcher_that_hands_off_and_whose_window_comes_late_is_never_put_in_a_terminal(self):
        desktop = mocked_desktop([])
        desktop.launch.return_value = launch_that(stopped=True)
        start = Start(desktop, app_list((1, [CHAT])))
        start.window_appearing_after(12, window("c", "chrome-chat.google.com-Default", "Chat", 1))
        outcome = start.run()
        desktop.launch_in_terminal.assert_not_called()
        self.assertEqual((outcome.started, outcome.unseen), (["Chat"], []))

    def test_a_command_that_fails_is_never_put_in_a_terminal(self):
        desktop = mocked_desktop([])
        desktop.launch.return_value = launch_that(stopped=True)
        start = Start(desktop, app_list((1, [TYPO])))
        outcome = start.run()
        desktop.launch_in_terminal.assert_not_called()
        start.store.save.assert_not_called()
        self.assertEqual(outcome.unseen, ["Typo"])

    def test_an_app_known_to_need_a_terminal_opens_in_one_at_once(self):
        desktop = mocked_desktop([])
        appearing_once_in_a_terminal(desktop, [window("t", TERMINAL, "foot", 2)])
        start = Start(desktop, app_list((2, [KNOWN_HELPER])))
        outcome = start.run()
        desktop.launch.assert_not_called()
        desktop.launch_in_terminal.assert_called_once_with("cd code && helper", 2, TERMINAL)
        self.assertEqual((outcome.unseen, start.clock.now), ([], 0.5))

    def test_a_folder_and_program_command_still_running_is_never_put_in_a_terminal(self):
        start = Start(mocked_desktop([]), app_list((2, [HELPER])))
        outcome = start.run()
        start.desktop.launch_in_terminal.assert_not_called()
        self.assertEqual(outcome.unseen, ["Helper"])

    def test_a_command_that_hands_its_window_over_at_once_is_not_put_in_a_terminal(self):
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


if __name__ == "__main__":
    unittest.main()
