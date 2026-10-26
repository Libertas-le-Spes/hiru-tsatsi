import unittest

from tests.entrypoints.mocked_services import Typed, mocked_services
from hiru_tsatsi.use_cases.ports import ConfigLeftAlone, SetUpFailed
from hiru_tsatsi.use_cases.setting_up import SetUp
from hiru_tsatsi.work_apps.shortcut import Keys

TURN_THEM = "Turn them on or off with `hiru-tsatsi window-titles on` or `off`."


class TheWindowTitlesCommand(unittest.TestCase):
    def test_with_no_choice_typed_it_only_says_which_it_is_and_why(self):
        services = mocked_services()
        services.window_titles.wanted.return_value = True
        services.window_titles.chosen.return_value = False
        typed = Typed(["window-titles"], services)
        services.window_titles.turn.assert_not_called()
        self.assertEqual(typed.printed, f"Window titles are on, because window-names is installed. {TURN_THEM}\n")

    def test_off_turns_them_off_once(self):
        services = mocked_services()
        services.window_titles.wanted.return_value = False
        services.window_titles.chosen.return_value = True
        typed = Typed(["window-titles", "off"], services)
        services.window_titles.turn.assert_called_once_with(False)
        self.assertEqual(typed.printed, f"Window titles are off, as you chose. {TURN_THEM}\n")


class TheSetUpCommand(unittest.TestCase):
    def test_says_which_shortcut_now_starts_the_apps(self):
        services = mocked_services()
        services.set_up.run.return_value = SetUp(Keys.parse("SUPER + ALT + U"), kept=False)
        typed = Typed(["set-up"], services)
        self.assertEqual(typed.exit_code, 0)
        self.assertTrue(typed.printed.startswith("SUPER + ALT + U now starts your work apps."))

    def test_a_desktop_problem_after_setting_up_fails_and_shows_it(self):
        services = mocked_services()
        services.set_up.run.side_effect = SetUpFailed("hiru-tsatsi.lua:1: bad")
        typed = Typed(["set-up"], services)
        self.assertEqual(typed.exit_code, 1)
        self.assertIn("hiru-tsatsi.lua:1: bad", typed.printed)

    def test_a_config_left_alone_fails_and_says_nothing_was_set_up(self):
        services = mocked_services()
        services.set_up.run.side_effect = ConfigLeftAlone("hyprland.lua changed meanwhile")
        typed = Typed(["set-up"], services)
        self.assertEqual((typed.exit_code, typed.printed), (1, "Nothing was set up: hyprland.lua changed meanwhile.\n"))


if __name__ == "__main__":
    unittest.main()
