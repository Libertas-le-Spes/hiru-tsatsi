import unittest

from tests.examples.app_lists import app_list
from tests.examples.home import RECOGNISING
from tests.examples.windows import window
from tests.use_cases.mocked_list import desktop_showing, store_holding
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.work_apps.app import App

GITLAB_COMMAND = 'omarchy-launch-webapp "https://gitlab.com/examplecorp/harbour/-/boards/1234567"'
RIDER_MAIN = App("Rider Main", "rider ~/code/harbour", "harbour")
RIDER_WINDOW = window("m", "jetbrains-rider", "harbour – /address-comments", 2)
GITLAB_WINDOW = window("g", "chrome-gitlab.com__examplecorp_harbour_-_boards_1234567-Default", "Issue Boards", 1)


def windows_given(open_windows, apps) -> list[str | None]:
    given = []
    for space in Overview(store_holding(apps), desktop_showing(open_windows), RECOGNISING).run():
        for view in space.apps:
            if view.window is None:
                given.append(None)
            else:
                given.append(view.window.address)
    return given


class TheOverview(unittest.TestCase):
    def test_each_app_gets_the_open_window_it_learned_and_no_other(self):
        moved = window("m", "jetbrains-rider", "harbour – x", 4)
        apps = app_list((1, [App("GitLab", GITLAB_COMMAND, "chrome-gitlab.com"), App("Chat", "chat", "chrome-chat")]),
                        (2, [RIDER_MAIN, App("Steam", "steam")]))
        self.assertEqual(windows_given([GITLAB_WINDOW, moved], apps), ["g", None, "m", None])

    def test_the_windows_to_choose_from_put_the_likeliest_first_and_leave_out_owned_ones(self):
        terminal = window("t", "foot", "~")
        apps = app_list((1, [App("GitLab", GITLAB_COMMAND)]), (2, [RIDER_MAIN]))
        overview = Overview(store_holding(apps), desktop_showing([terminal, RIDER_WINDOW, GITLAB_WINDOW]), RECOGNISING)
        addresses = []
        for candidate in overview.candidates(1, 0):
            addresses.append(candidate.address)
        self.assertEqual(addresses, ["g", "t"])

    def test_the_windows_to_choose_from_leave_out_its_program_running_in_another_folder(self):
        here = window("h", "foot", "~", 2, "helper", "/home/sam/code")
        elsewhere = window("e", "foot", "~", 2, "helper", "/home/sam/other")
        apps = app_list((2, [App("Helper", "cd code && helper")]))
        overview = Overview(store_holding(apps), desktop_showing([elsewhere, here]), RECOGNISING)
        addresses = []
        for candidate in overview.candidates(2, 0):
            addresses.append(candidate.address)
        self.assertEqual(addresses, ["h"])

    def test_a_session_opened_by_hand_is_that_apps_window(self):
        by_hand = window("h", "foot", "✳ Some talk", 2, "helper", "/home/sam/code")
        self.assertEqual(windows_given([by_hand], app_list((2, [App("Helper", "cd code && helper")]))), ["h"])


if __name__ == "__main__":
    unittest.main()
