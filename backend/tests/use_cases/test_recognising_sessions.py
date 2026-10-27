import unittest

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.mocked_list import desktop_showing, saved_once
from tests.use_cases.starting_scene import CHAT, HELPER, Start, appearing_once_launched
from tests.use_cases.terminal_examples import KNOWN_HELPER
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.terminal_use import TerminalUse


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

    def test_a_session_of_the_same_program_in_another_folder_is_never_taken_by_its_title(self):
        other_project = window("o", "foot", "✳ Claude Code", 4, "helper", "/home/sam/other")
        start = Start(desktop_showing([]), app_list((2, [App("Helper", "cd code && helper")])))
        appearing_once_launched(start.desktop, [], [other_project])
        outcome = start.run()
        start.desktop.move.assert_not_called()
        start.store.save.assert_not_called()
        self.assertEqual(outcome.unseen, ["Helper"])

    def test_a_hand_edited_terminal_mark_on_another_kind_of_command_starts_it_plainly(self):
        marked = App("Chat", CHAT.command, "hiru-tsatsi.chat-1a2b3c4d", terminal=TerminalUse.OPENS_IN_ONE)
        start = Start(desktop_showing([]), app_list((1, [marked])))
        start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        start.desktop.launch.assert_called_once_with(CHAT.command, 1)

    def test_an_app_that_is_itself_a_terminal_learns_its_window_with_a_shell_inside(self):
        own = window("f", "foot", "sam@desk:/tmp", 9, "bash", "/tmp")
        start = Start(desktop_showing([]), app_list((9, [App("Own terminal", "cd /tmp && foot")])))
        appearing_once_launched(start.desktop, [], [own])
        outcome = start.run()
        self.assertEqual(outcome.unseen, [])
        self.assertEqual(saved_once(start.store).placements()[0].app.learned_window, "foot")


if __name__ == "__main__":
    unittest.main()
