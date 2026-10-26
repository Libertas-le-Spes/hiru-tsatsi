import unittest

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.examples.home import RECOGNISING
from tests.use_cases.mocked_list import desktop_showing, store_holding
from hiru_tsatsi.presenters.status_lines import status_line
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.work_apps.app import App

GITLAB_COMMAND = 'omarchy-launch-webapp "https://gitlab.com/examplecorp/harbour/-/boards/1234567"'
RIDER_MAIN = App("Rider Main", "rider ~/code/harbour", "harbour")
RIDER_WINDOW = window("m", "jetbrains-rider", "harbour – /address-comments", 2)
GITLAB_WINDOW = window("g", "chrome-gitlab.com__examplecorp_harbour_-_boards_1234567-Default", "Issue Boards", 1)


def status_lines(open_windows, apps) -> list[str]:
    lines = []
    for space in Overview(store_holding(apps), desktop_showing(open_windows), RECOGNISING).run():
        for view in space.apps:
            lines.append(status_line(view))
    return lines


class TheOverview(unittest.TestCase):
    def test_each_app_shows_where_its_window_is(self):
        moved = window("m", "jetbrains-rider", "harbour – x", 4)
        apps = app_list((1, [App("GitLab", GITLAB_COMMAND, "chrome-gitlab.com"), App("Chat", "chat", "chrome-chat")]),
                        (2, [RIDER_MAIN, App("Steam", "steam")]))
        self.assertEqual(status_lines([GITLAB_WINDOW, moved], apps),
                         ["✓ Issue Boards, open on workspace 1",
                          "Recognised when it opens",
                          "✓ harbour – x, open on workspace 4 (moved to 2 when you start)",
                          "Will be recognised the first time Hiru Tsatsi starts it"])

    def test_a_session_opened_by_hand_shows_as_open(self):
        by_hand = window("h", "foot", "✳ Some talk", 2, "helper", "/home/sam/code")
        self.assertEqual(status_lines([by_hand], app_list((2, [App("Helper", "cd code && helper")]))),
                         ["✓ ✳ Some talk, open on workspace 2"])

    def test_an_app_that_opens_in_a_terminal_says_so_while_closed(self):
        helper = App("Helper", "cd code && helper", "hiru-tsatsi.2-0-helper", in_terminal=True)
        self.assertEqual(status_lines([], app_list((2, [helper]))), ["Opens in a terminal, recognised when it opens"])

    def test_the_windows_to_choose_from_put_the_likeliest_first_and_leave_out_owned_ones(self):
        terminal = window("t", "foot", "~")
        apps = app_list((1, [App("GitLab", GITLAB_COMMAND)]), (2, [RIDER_MAIN]))
        overview = Overview(store_holding(apps), desktop_showing([terminal, RIDER_WINDOW, GITLAB_WINDOW]), RECOGNISING)
        addresses = []
        for candidate in overview.candidates(1, 0):
            addresses.append(candidate.address)
        self.assertEqual(addresses, ["g", "t"])


if __name__ == "__main__":
    unittest.main()
