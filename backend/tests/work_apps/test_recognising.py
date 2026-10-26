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


if __name__ == "__main__":
    unittest.main()
