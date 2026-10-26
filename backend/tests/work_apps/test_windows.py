import unittest

from tests.fakes.desktop import window
from hiru_tsatsi.work_apps.window_guessing import guess_window
from hiru_tsatsi.work_apps.window_naming import name_for
from hiru_tsatsi.work_apps.windows import belongs_to

GITLAB = window("g", "chrome-gitlab.com__examplecorp_harbour_-_boards_1234567-Default", "Issue Boards · Lantern - Tide · GitLab")
CHAT = window("c", "chrome-chat.google.com__u_2_app_home-Default", "Chat")
MAIN = window("m", "jetbrains-rider", "harbour – /address-comments", 2)
REVIEW = window("r", "jetbrains-rider", "lantern-review – Sam's MR!42", 3)
MUSIC = window("y", "chrome-music.youtube.com__-Default", "YouTube Music", 5)
GITHUB = window("h", "chrome-github.com__-Default", "Trending repositories on GitHub today", 6)
TERMINAL = window("t", "foot", "~", 4)
SESSION = [MAIN, GITLAB, MUSIC, CHAT, REVIEW, TERMINAL, GITHUB]

APPS = {
    ("GitLab", 'omarchy-launch-webapp "https://gitlab.com/examplecorp/harbour/-/boards/1234567?iteration_id=Current"'): GITLAB,
    ("Chat", "omarchy-launch-webapp https://chat.google.com/u/2/app/home"): CHAT,
    ("Rider Main", "rider ~/RiderProjects/harbour"): MAIN,
    ("Rider Review", "rider ~/RiderProjects/lantern-review"): REVIEW,
    ("YouTube Music", "omarchy-launch-webapp https://music.youtube.com/"): MUSIC,
    ("Github", "omarchy-launch-webapp https://github.com"): GITHUB,
}


class GuessingAWindowFromItsCommand(unittest.TestCase):
    def test_every_app_in_a_real_session_finds_its_own_window(self):
        for (name, command), expected in APPS.items():
            with self.subTest(name=name):
                self.assertEqual(guess_window(name, command, SESSION), expected)

    def test_the_saved_name_finds_the_same_window_again(self):
        for (_, command), expected in APPS.items():
            name = name_for(expected, SESSION, command)
            with self.subTest(name=name):
                self.assertEqual(next(w for w in SESSION if belongs_to(w, name)), expected)

    def test_a_web_app_keeps_its_class_and_rider_keeps_its_project(self):
        self.assertEqual(name_for(GITHUB, SESSION, "omarchy-launch-webapp https://github.com"), "chrome-github.com__-Default")
        self.assertEqual(name_for(MAIN, [MAIN], "rider ~/RiderProjects/harbour"), "harbour")

    def test_the_name_finds_a_window_the_command_says_nothing_about(self):
        mail = window("m", "thunderbird", "Inbox - Thunderbird")
        self.assertEqual(guess_window("Thunderbird", "/usr/lib/mail-client --profile work", [TERMINAL, mail]), mail)

    def test_the_name_never_decides_what_is_remembered(self):
        self.assertEqual(name_for(MAIN, [MAIN], "rider ~/RiderProjects/harbour"), "harbour")
        self.assertNotEqual(name_for(MAIN, [MAIN], "rider ~/RiderProjects/harbour"), "jetbrains-rider")

    def test_no_guess_without_a_clear_answer(self):
        cases = {
            "only the other project open": ("rider ~/RiderProjects/lantern-review", [MAIN]),
            "nothing matches": ("steam", [TERMINAL]),
            "two equally good windows": ("steam", [window("a", "steam", "Steam"), window("b", "steamwebhelper", "x")]),
            "no windows": ("steam", []),
        }
        for case, (command, windows) in cases.items():
            with self.subTest(case=case):
                self.assertIsNone(guess_window("", command, windows))

    def test_a_bare_program_is_matched_by_its_own_name(self):
        steam = window("s", "steam", "Steam")
        self.assertEqual(guess_window("", "steam", [TERMINAL, steam]), steam)


if __name__ == "__main__":
    unittest.main()
