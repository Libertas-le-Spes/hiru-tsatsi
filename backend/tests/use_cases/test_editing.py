import unittest

from tests.fakes import FakeDesktop, FakeStore, app_list, window
from hiru_tsatsi.use_cases.editing import EditAppList
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.presenters.status_lines import status_line
from hiru_tsatsi.work_apps.app_list import App

GITLAB_COMMAND = 'omarchy-launch-webapp "https://gitlab.com/examplecorp/harbour/-/boards/1234567"'
RIDER_MAIN = App("Rider Main", "rider ~/RiderProjects/harbour", "harbour")
RIDER_WINDOW = window("m", "jetbrains-rider", "harbour – /address-comments", 2)
GITLAB_WINDOW = window("g", "chrome-gitlab.com__examplecorp_harbour_-_boards_1234567-Default", "Issue Boards", 1)


def editing(open_windows, apps):
    store = FakeStore(apps)
    desktop = FakeDesktop(open_windows)
    return EditAppList(store, desktop), Overview(store, desktop), store


class AddingAnApp(unittest.TestCase):
    def test_an_app_that_is_already_open_is_recognised_at_once(self):
        edit, _, store = editing([RIDER_WINDOW, GITLAB_WINDOW], app_list((1, []), (2, [RIDER_MAIN])))
        edit.add_app(1, "GitLab", GITLAB_COMMAND)
        self.assertEqual(store.apps.workspace(1).apps[0].learned_window, GITLAB_WINDOW.window_class)

    def test_a_window_another_app_owns_is_never_taken(self):
        edit, _, store = editing([RIDER_WINDOW], app_list((1, []), (2, [RIDER_MAIN])))
        edit.add_app(1, "GitLab", GITLAB_COMMAND)
        self.assertEqual(store.apps.workspace(1).apps[0].learned_window, "")

    def test_choosing_a_window_by_hand_and_forgetting_it(self):
        edit, _, store = editing([GITLAB_WINDOW], app_list((1, [App("Boards", "some-browser --board")])))
        edit.choose_window(1, 0, "g")
        self.assertEqual(store.apps.workspace(1).apps[0].learned_window, GITLAB_WINDOW.window_class)
        edit.forget_window(1, 0)
        self.assertEqual(store.apps.workspace(1).apps[0].learned_window, "")


class TheOverview(unittest.TestCase):
    def test_each_app_shows_where_its_window_is(self):
        moved = window("m", "jetbrains-rider", "harbour – x", 4)
        apps = app_list((1, [App("GitLab", GITLAB_COMMAND, "chrome-gitlab.com"), App("Chat", "chat", "chrome-chat")]),
                        (2, [RIDER_MAIN, App("Steam", "steam")]))
        _, overview, _ = editing([GITLAB_WINDOW, moved], apps)
        lines = [status_line(view) for space in overview.run() for view in space.apps]
        self.assertEqual(lines, ["✓ Issue Boards, open on workspace 1",
                                 "Recognised when it opens",
                                 "✓ harbour – x, open on workspace 4 (moved to 2 when you start)",
                                 "Will be recognised the first time Hiru Tsatsi starts it"])

    def test_the_windows_to_choose_from_put_the_likeliest_first_and_leave_out_owned_ones(self):
        terminal = window("t", "foot", "~")
        apps = app_list((1, [App("GitLab", GITLAB_COMMAND)]), (2, [RIDER_MAIN]))
        _, overview, _ = editing([terminal, RIDER_WINDOW, GITLAB_WINDOW], apps)
        self.assertEqual([w.address for w in overview.candidates(1, 0)], ["g", "t"])


if __name__ == "__main__":
    unittest.main()
