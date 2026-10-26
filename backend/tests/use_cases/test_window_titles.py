import unittest
from unittest.mock import Mock, create_autospec

from tests.examples.windows import window
from hiru_tsatsi.use_cases.ports import SettingsStore, WindowNames
from hiru_tsatsi.use_cases.window_titles import NamesWhenWanted, WindowTitles


def titles(chosen: bool | None, installed: bool) -> WindowTitles:
    settings = create_autospec(SettingsStore, instance=True)
    settings.window_titles.return_value = chosen
    return WindowTitles(settings, Mock(return_value=installed))


class ChoosingWhetherToNameWindows(unittest.TestCase):
    def test_with_nothing_chosen_it_follows_whether_window_names_is_installed(self):
        self.assertTrue(titles(chosen=None, installed=True).wanted())
        self.assertFalse(titles(chosen=None, installed=False).wanted())

    def test_a_choice_wins_without_asking_what_is_installed(self):
        chosen = titles(chosen=False, installed=True)
        self.assertFalse(chosen.wanted())
        chosen.namer_installed.assert_not_called()

    def test_turning_it_off_saves_the_choice_once(self):
        chosen = titles(chosen=None, installed=True)
        chosen.turn(False)
        chosen.settings.set_window_titles.assert_called_once_with(False)


class NamingOnlyWhenWanted(unittest.TestCase):
    def test_nothing_is_written_while_it_is_off(self):
        names = create_autospec(WindowNames, instance=True)
        NamesWhenWanted(titles(chosen=False, installed=True), names).record(window("0xa", "steam"), "Steam")
        names.record.assert_not_called()

    def test_names_are_written_while_it_is_on(self):
        names = create_autospec(WindowNames, instance=True)
        steam = window("0xa", "steam")
        NamesWhenWanted(titles(chosen=None, installed=True), names).record(steam, "Steam")
        names.record.assert_called_once_with(steam, "Steam")


if __name__ == "__main__":
    unittest.main()
