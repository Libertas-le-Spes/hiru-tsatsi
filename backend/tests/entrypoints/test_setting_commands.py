import unittest

from tests.entrypoints.mocked_app import Typed, mocked_app
from hiru_tsatsi.use_cases.ports import ConfigLeftAlone, SetUpFailed
from hiru_tsatsi.use_cases.setting_up import SetUp
from hiru_tsatsi.work_apps.shortcut import Keys

TURN_THEM = "Turn them on or off with `hiru-tsatsi window-titles on` or `off`."


class TheWindowTitlesCommand(unittest.TestCase):
    def test_with_no_choice_typed_it_only_says_which_it_is_and_why(self):
        app = mocked_app()
        app.window_titles.wanted.return_value = True
        app.window_titles.chosen.return_value = False
        typed = Typed(["window-titles"], app)
        app.window_titles.turn.assert_not_called()
        self.assertEqual(typed.printed, f"Window titles are on, because window-names is installed. {TURN_THEM}\n")

    def test_off_turns_them_off_once(self):
        app = mocked_app()
        app.window_titles.wanted.return_value = False
        app.window_titles.chosen.return_value = True
        typed = Typed(["window-titles", "off"], app)
        app.window_titles.turn.assert_called_once_with(False)
        self.assertEqual(typed.printed, f"Window titles are off, as you chose. {TURN_THEM}\n")


class TheSetUpCommand(unittest.TestCase):
    def test_says_which_shortcut_now_starts_the_apps(self):
        app = mocked_app()
        app.set_up.run.return_value = SetUp(Keys.parse("SUPER + ALT + U"), kept=False)
        typed = Typed(["set-up"], app)
        self.assertEqual(typed.exit_code, 0)
        self.assertTrue(typed.printed.startswith("SUPER + ALT + U now starts your work apps."))

    def test_a_desktop_problem_after_setting_up_fails_and_shows_it(self):
        app = mocked_app()
        app.set_up.run.side_effect = SetUpFailed("hiru-tsatsi.lua:1: bad")
        typed = Typed(["set-up"], app)
        self.assertEqual(typed.exit_code, 1)
        self.assertIn("hiru-tsatsi.lua:1: bad", typed.printed)

    def test_a_config_left_alone_fails_and_says_nothing_was_set_up(self):
        app = mocked_app()
        app.set_up.run.side_effect = ConfigLeftAlone("hyprland.lua changed meanwhile")
        typed = Typed(["set-up"], app)
        self.assertEqual((typed.exit_code, typed.printed), (1, "Nothing was set up: hyprland.lua changed meanwhile.\n"))


if __name__ == "__main__":
    unittest.main()
