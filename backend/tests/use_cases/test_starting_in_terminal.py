import unittest

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.mocked_list import desktop_showing, saved_once
from tests.use_cases.starting_scene import CHAT, HELPER, HELPERS_TERMINAL, MAIN, Start, appearing_once_launched
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.windows import Window

KNOWN_HELPER = App("Helper", "cd code && helper", HELPERS_TERMINAL, in_terminal=True)
EDITOR = App("Editor", "cd code && editor .")
FAILING = App("Failing", "chromiun --app=https://example.org/")


def helper_running_in(window_class: str, workspace: int) -> Window:
    return window("t", window_class, "✳ Helper", workspace, "helper", "/home/sam/code")


def a_shell_waiting_in(window_class: str, workspace: int) -> Window:
    return window("t", window_class, "foot", workspace, "sh", "/home/sam")


class TryingATerminal(unittest.TestCase):
    def test_a_folder_and_program_command_that_stops_without_a_window_is_opened_in_a_terminal(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        start.window_appearing_in_its_terminal(helper_running_in(HELPERS_TERMINAL, 2))
        outcome = start.run()
        self.assertTrue(start.opened_in_its_terminal(HELPER, 2))
        self.assertEqual((outcome.in_terminal, outcome.unseen), (["Helper"], []))

    def test_needing_a_terminal_is_saved_once_the_program_is_seen_running_in_it(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        start.window_appearing_in_its_terminal(helper_running_in(HELPERS_TERMINAL, 2))
        start.run()
        remembered = saved_once(start.store).placements()[0].app
        self.assertEqual((remembered.in_terminal, remembered.learned_window), (True, HELPERS_TERMINAL))

    def test_needing_a_terminal_is_saved_when_the_program_starts_a_moment_after_its_window(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)

        def shell_first_then_the_program() -> list[Window]:
            if not start.opened_in_terminal():
                return []
            if start.clock.now < 12.0:
                return [a_shell_waiting_in(HELPERS_TERMINAL, 2)]
            return [helper_running_in(HELPERS_TERMINAL, 2)]

        start.desktop.windows.side_effect = shell_first_then_the_program
        outcome = start.run()
        self.assertEqual(outcome.in_terminal, ["Helper"])
        self.assertTrue(saved_once(start.store).placements()[0].app.in_terminal)

    def test_a_folder_and_program_command_with_a_typo_is_not_remembered_as_a_terminal_app(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        start.window_appearing_in_its_terminal(a_shell_waiting_in(HELPERS_TERMINAL, 2))
        outcome = start.run()
        start.store.save.assert_not_called()
        self.assertEqual(outcome.in_terminal, [])

    def test_nothing_is_saved_when_the_terminal_window_never_appears(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        outcome = start.run()
        self.assertEqual(len(start.opened_in_terminal()), 1)
        start.store.save.assert_not_called()
        self.assertEqual((outcome.in_terminal, outcome.unseen), ([], ["Helper"]))

    def test_a_window_that_arrives_just_before_ten_seconds_wins_over_a_terminal(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        start.window_appearing_after(9.8, helper_running_in("foot", 2))
        outcome = start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual((outcome.started, outcome.unseen), (["Helper"], []))


class NeverTryingATerminal(unittest.TestCase):
    def test_a_folder_and_program_editor_with_its_own_window_still_learns_that_window(self):
        desktop = desktop_showing([])
        appearing_once_launched(desktop, [], [window("e", "code", "harbour - Editor", 2)])
        start = Start(desktop, app_list((2, [EDITOR])), stops=True)
        start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual(saved_once(start.store).placements()[0].app.learned_window, "code")

    def test_a_command_of_any_other_shape_is_never_put_in_a_terminal_even_when_it_stops(self):
        start = Start(desktop_showing([]), app_list((1, [FAILING])), stops=True)
        outcome = start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual(outcome.unseen, ["Failing"])

    def test_a_command_of_any_other_shape_is_launched_without_being_watched(self):
        start = Start(desktop_showing([]), app_list((1, [CHAT])))
        start.run()
        start.launches.new.assert_not_called()
        start.desktop.launch.assert_called_once_with(CHAT.command, 1)

    def test_a_folder_and_program_command_still_running_is_never_put_in_a_terminal(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=False)
        outcome = start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual(outcome.unseen, ["Helper"])

    def test_an_app_known_to_need_a_terminal_opens_in_one_at_once_without_a_plain_try(self):
        start = Start(desktop_showing([]), app_list((2, [KNOWN_HELPER])))
        start.window_appearing_in_its_terminal(helper_running_in(HELPERS_TERMINAL, 2))
        outcome = start.run()
        self.assertTrue(start.opened_in_its_terminal(KNOWN_HELPER, 2))
        start.launches.new.assert_not_called()
        self.assertEqual((outcome.unseen, start.clock.now), ([], 0.5))


class FindingSessionsOpenedByHand(unittest.TestCase):
    def test_a_session_in_the_right_folder_counts_as_open_and_is_moved(self):
        by_hand = window("h", "foot", "✳ Some talk", 4, "helper", "/home/sam/code")
        start = Start(desktop_showing([by_hand]), app_list((2, [HELPER])))
        outcome = start.run()
        start.desktop.launch.assert_not_called()
        start.desktop.move.assert_called_once_with(by_hand, 2)
        start.store.save.assert_not_called()
        self.assertEqual(outcome.already_open, ["Helper"])

    def test_a_terminal_app_finds_its_session_opened_by_hand(self):
        start = Start(desktop_showing([window("h", "foot", "✳ Some talk", 2, "helper", "/home/sam/code")]),
                      app_list((2, [KNOWN_HELPER])))
        outcome = start.run()
        start.desktop.launch.assert_not_called()
        self.assertEqual(outcome.already_open, ["Helper"])

    def test_a_rider_window_is_not_mistaken_for_a_terminal_session(self):
        start = Start(desktop_showing([window("m", "jetbrains-rider", "harbour – x", 2)]), app_list((2, [MAIN])))
        start.run()
        self.assertEqual(start.opened_in_terminal(), [])


if __name__ == "__main__":
    unittest.main()
