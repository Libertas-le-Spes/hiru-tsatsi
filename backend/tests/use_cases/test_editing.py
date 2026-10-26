import unittest

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.examples.home import RECOGNISING
from tests.use_cases.mocked_list import desktop_showing, saved_once, store_holding
from hiru_tsatsi.use_cases.editing import EditAppList
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.refusals import NothingThere

GITLAB_COMMAND = 'omarchy-launch-webapp "https://gitlab.com/examplecorp/harbour/-/boards/1234567"'
RIDER_MAIN = App("Rider Main", "rider ~/code/harbour", "harbour")
RIDER_WINDOW = window("m", "jetbrains-rider", "harbour – /address-comments", 2)
GITLAB_WINDOW = window("g", "chrome-gitlab.com__examplecorp_harbour_-_boards_1234567-Default", "Issue Boards", 1)
BOARDS = App("Boards", "some-browser --board")


def editing(open_windows, apps):
    store = store_holding(apps)
    return EditAppList(store, desktop_showing(open_windows), RECOGNISING), store


class AddingAnApp(unittest.TestCase):
    def test_an_app_that_is_already_open_is_recognised_at_once(self):
        edit, store = editing([RIDER_WINDOW, GITLAB_WINDOW], app_list((1, []), (2, [RIDER_MAIN])))
        edit.add_app(1, "GitLab", GITLAB_COMMAND)
        self.assertEqual(saved_once(store).workspace(1).apps[0].learned_window, GITLAB_WINDOW.window_class)

    def test_a_window_another_app_owns_is_never_taken_even_when_it_matches(self):
        edit, store = editing([RIDER_WINDOW], app_list((1, []), (2, [RIDER_MAIN])))
        edit.add_app(1, "Second Rider", "rider ~/code/harbour")
        self.assertEqual(saved_once(store).workspace(1).apps[0].learned_window, "")


class ChoosingAWindowByHand(unittest.TestCase):
    def test_the_chosen_window_is_learned_and_saved_once(self):
        edit, store = editing([GITLAB_WINDOW], app_list((1, [BOARDS])))
        edit.choose_window(1, 0, "g")
        self.assertEqual(saved_once(store).workspace(1).apps[0].learned_window, GITLAB_WINDOW.window_class)

    def test_a_window_that_has_closed_meanwhile_is_refused_and_nothing_is_saved(self):
        edit, store = editing([], app_list((1, [BOARDS])))
        with self.assertRaises(NothingThere):
            edit.choose_window(1, 0, "g")
        store.save.assert_not_called()

    def test_forgetting_clears_the_learned_window_and_saves_once(self):
        edit, store = editing([], app_list((1, [App("Boards", "some-browser --board", "chrome-gitlab")])))
        edit.forget_window(1, 0)
        self.assertEqual(saved_once(store).workspace(1).apps[0].learned_window, "")

    def test_a_folder_and_program_app_never_learns_another_folders_session_by_its_title(self):
        other_project = window("o", "foot", "✳ Claude Code", 4, "claude", "/home/sam/other")
        edit, store = editing([other_project], app_list((1, [])))
        edit.add_app(1, "Claude Code", "cd code && claude")
        self.assertEqual(saved_once(store).workspace(1).apps[0].learned_window, "")

    def test_a_folder_and_program_app_added_while_its_session_is_open_learns_no_title(self):
        session = window("s", "foot", "✳ Claude Code: fixing the login page", 4, "claude", "/home/sam/code")
        edit, store = editing([session], app_list((1, [])))
        edit.add_app(1, "Claude Code", "cd code && claude")
        self.assertEqual(saved_once(store).workspace(1).apps[0].learned_window, "")


if __name__ == "__main__":
    unittest.main()
