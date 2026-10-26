import unittest

from tests.fakes.app_lists import app_list
from tests.fakes.desktop import FakeDesktop, window
from tests.use_cases.starting_examples import CHAT, HELPER, MAIN, start
from hiru_tsatsi.use_cases.app_starts import OwnWindowStart
from hiru_tsatsi.work_apps.app import App


class StartingAppsThatNeedATerminal(unittest.TestCase):
    def test_a_command_that_stops_without_a_window_is_opened_again_in_a_terminal(self):
        desktop = FakeDesktop([], stopping={HELPER.command})
        outcome, store, _ = start(desktop, app_list((2, [HELPER])))
        self.assertEqual(desktop.in_terminal, [("cd code && helper", 2, "hiru-tsatsi.2-0-helper")])
        self.assertEqual((outcome.in_terminal, outcome.unseen), (["Helper"], []))

    def test_remembers_that_the_app_opens_in_a_terminal(self):
        _, store, _ = start(FakeDesktop([], stopping={HELPER.command}), app_list((2, [HELPER])))
        remembered = store.apps.placements()[0].app
        self.assertEqual((remembered.in_terminal, remembered.learned_window), (True, "hiru-tsatsi.2-0-helper"))

    def test_an_app_known_to_need_a_terminal_opens_in_one_at_once(self):
        known = App("Helper", "cd code && helper", "hiru-tsatsi.2-0-helper", in_terminal=True)
        desktop = FakeDesktop([])
        outcome, _, clock = start(desktop, app_list((2, [known])))
        self.assertEqual(desktop.launched, [])
        self.assertEqual(desktop.in_terminal, [("cd code && helper", 2, "hiru-tsatsi.2-0-helper")])
        self.assertEqual((outcome.unseen, clock.now), ([], 0.5))

    def test_a_slow_app_still_running_is_never_put_in_a_terminal(self):
        desktop = FakeDesktop([])
        outcome, store, _ = start(desktop, app_list((2, [MAIN])))
        self.assertEqual((desktop.in_terminal, outcome.unseen), ([], ["Rider Main"]))
        self.assertFalse(store.apps.placements()[0].app.in_terminal)

    def test_a_command_that_hands_its_window_to_a_running_app_is_not_put_in_a_terminal(self):
        handed_over = window("c", "chrome-chat.google.com-Default", "Chat", 1)
        desktop = FakeDesktop([], {CHAT.command: [handed_over]}, stopping={CHAT.command})
        outcome, _, _ = start(desktop, app_list((1, [CHAT])))
        self.assertEqual((desktop.in_terminal, outcome.started, outcome.unseen), ([], ["Chat"], []))

    def test_a_session_opened_by_hand_in_the_right_folder_counts_as_open(self):
        by_hand = window("h", "foot", "✳ Some talk", 4, "helper", "/home/sam/code")
        desktop = FakeDesktop([by_hand])
        outcome, store, _ = start(desktop, app_list((2, [HELPER])))
        self.assertEqual((desktop.launched, desktop.in_terminal), ([], []))
        self.assertEqual((outcome.already_open, desktop.moves), (["Helper"], [("h", 2)]))
        self.assertEqual(store.apps.placements()[0].app.learned_window, "")

    def test_a_terminal_app_finds_its_session_opened_by_hand(self):
        known = App("Helper", "cd code && helper", "hiru-tsatsi.2-0-helper", in_terminal=True)
        desktop = FakeDesktop([window("h", "foot", "✳ Some talk", 2, "helper", "/home/sam/code")])
        outcome, _, _ = start(desktop, app_list((2, [known])))
        self.assertEqual((desktop.in_terminal, outcome.already_open), ([], ["Helper"]))

    def test_waits_ten_seconds_after_launching_before_deciding(self):
        class Stopped:
            def stopped(self):
                return True
        launched = OwnWindowStart(app_list((2, [HELPER])).placements()[0], Stopped(), since=100.0)
        self.assertEqual((launched.needs_terminal(109.9), launched.needs_terminal(110.0)), (False, True))


if __name__ == "__main__":
    unittest.main()
