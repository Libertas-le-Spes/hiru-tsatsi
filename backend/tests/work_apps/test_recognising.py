import unittest

from tests.examples.windows import window
from tests.examples.home import RECOGNISING
from hiru_tsatsi.work_apps.app import App

HARBOUR = App("Harbour", "cd code/harbour && helper")
LANTERN_WINDOW = window("a", "foot", "✳ Some talk", 3, "helper", "/home/sam/code/lantern")
HARBOUR_WINDOW = window("b", "foot", "✳ Other talk", 2, "helper", "/home/sam/code/harbour")


class RecognisingAnAppsWindow(unittest.TestCase):
    def test_by_the_program_and_folder_inside_it_whatever_its_title(self):
        found = RECOGNISING.known_window(HARBOUR, [LANTERN_WINDOW, HARBOUR_WINDOW], set())
        self.assertEqual(found.address, "b")

    def test_a_window_already_claimed_is_not_taken_twice(self):
        self.assertIsNone(RECOGNISING.known_window(HARBOUR, [LANTERN_WINDOW, HARBOUR_WINDOW], {"b"}))

    def test_by_its_learned_name_when_the_command_says_nothing_about_what_runs_inside(self):
        chat = App("Chat", "chat-app", "chrome-chat")
        found = RECOGNISING.known_window(chat, [window("c", "chrome-chat-Default", "Chat", 1)], set())
        self.assertEqual(found.address, "c")

    def test_an_app_that_knows_nothing_finds_nothing(self):
        self.assertIsNone(RECOGNISING.known_window(App("Steam", "steam"), [window("s", "steam", "Steam")], set()))

    def test_a_terminal_app_finds_only_the_window_with_exactly_its_name(self):
        terminal = App("Helper", "helper --tui", "hiru-tsatsi.helper-1a2b3c4d", in_terminal=True)
        longer_name = window("x", "hiru-tsatsi.helper-1a2b3c4d5e", "foot")
        page_titled_like_it = window("p", "chromium", "hiru-tsatsi.helper-1a2b3c4d")
        exact = window("t", "hiru-tsatsi.helper-1a2b3c4d", "foot")
        found = RECOGNISING.known_window(terminal, [longer_name, page_titled_like_it, exact], set())
        self.assertEqual(found.address, "t")

    def test_a_program_name_longer_than_linux_keeps_still_matches(self):
        long_name = App("Long", "cd code/harbour && a-very-long-program-name")
        cut_by_linux = window("l", "foot", "", 2, "a-very-long-pro", "/home/sam/code/harbour")
        self.assertTrue(RECOGNISING.runs_inside(long_name, cut_by_linux))

    def test_an_editor_window_with_nothing_readable_inside_does_not_run_the_app(self):
        self.assertFalse(RECOGNISING.runs_inside(HARBOUR, window("e", "code", "harbour", 2)))


if __name__ == "__main__":
    unittest.main()
