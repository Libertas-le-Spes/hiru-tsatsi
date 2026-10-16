import unittest

from tests.fakes import window
from workbench.work_apps.windows import belongs_to, guess_window, name_for

GITLAB = window("g", "chrome-gitlab.com__examplecorp_harbour_-_boards_1234567-Default", "Issue Boards · Lantern - Tide · GitLab")
CHAT = window("c", "chrome-chat.google.com__u_2_app_home-Default", "Chat")
MAIN = window("m", "jetbrains-rider", "harbour – /address-comments", 2)
REVIEW = window("r", "jetbrains-rider", "lantern-review – Sam's MR!42", 3)
MUSIC = window("y", "chrome-music.youtube.com__-Default", "YouTube Music", 5)
GITHUB = window("h", "chrome-github.com__-Default", "Trending repositories on GitHub today", 6)
TERMINAL = window("t", "foot", "~", 4)
SESSION = [MAIN, GITLAB, MUSIC, CHAT, REVIEW, TERMINAL, GITHUB]

COMMANDS = {
    'omarchy-launch-webapp "https://gitlab.com/examplecorp/harbour/-/boards/1234567?iteration_id=Current"': GITLAB,
    "omarchy-launch-webapp https://chat.google.com/u/2/app/home": CHAT,
    "rider ~/RiderProjects/harbour": MAIN,
    "rider ~/RiderProjects/lantern-review": REVIEW,
    "omarchy-launch-webapp https://music.youtube.com/": MUSIC,
    "omarchy-launch-webapp https://github.com": GITHUB,
}


class GuessingAWindowFromItsCommand(unittest.TestCase):
    def test_every_app_in_a_real_session_finds_its_own_window(self):
        for command, expected in COMMANDS.items():
            with self.subTest(command=command):
                self.assertEqual(guess_window(command, SESSION), expected)

    def test_the_saved_name_finds_the_same_window_again(self):
        for command, expected in COMMANDS.items():
            name = name_for(expected, SESSION, command)
            with self.subTest(name=name):
                self.assertEqual(next(w for w in SESSION if belongs_to(w, name)), expected)

    def test_a_web_app_keeps_its_class_and_rider_keeps_its_project(self):
        self.assertEqual(name_for(GITHUB, SESSION, "omarchy-launch-webapp https://github.com"), "chrome-github.com__-Default")
        self.assertEqual(name_for(MAIN, [MAIN], "rider ~/RiderProjects/harbour"), "harbour")

    def test_no_guess_without_a_clear_answer(self):
        cases = {
            "only the other project open": ("rider ~/RiderProjects/lantern-review", [MAIN]),
            "nothing matches": ("steam", [TERMINAL]),
            "two equally good windows": ("steam", [window("a", "steam", "Steam"), window("b", "steamwebhelper", "x")]),
            "no windows": ("steam", []),
        }
        for case, (command, windows) in cases.items():
            with self.subTest(case=case):
                self.assertIsNone(guess_window(command, windows))

    def test_a_bare_program_is_matched_by_its_own_name(self):
        steam = window("s", "steam", "Steam")
        self.assertEqual(guess_window("steam", [TERMINAL, steam]), steam)


if __name__ == "__main__":
    unittest.main()
