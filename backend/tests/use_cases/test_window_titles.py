import unittest

from tests.fakes import FakeNames, FakeSettings, window
from hiru_tsatsi.use_cases.window_titles import NamesWhenWanted, WindowTitles


def titles(chosen=None, installed=True):
    return WindowTitles(FakeSettings(chosen), lambda: installed)


class ChoosingWhetherToNameWindows(unittest.TestCase):
    def test_with_nothing_chosen_it_follows_whether_window_names_is_installed(self):
        self.assertTrue(titles(installed=True).wanted())
        self.assertFalse(titles(installed=False).wanted())

    def test_a_choice_wins_over_what_is_installed(self):
        self.assertFalse(titles(chosen=False, installed=True).wanted())
        self.assertTrue(titles(chosen=True, installed=False).wanted())

    def test_turning_it_off_is_remembered(self):
        chosen = titles(installed=True)
        chosen.turn(False)
        self.assertEqual((chosen.wanted(), chosen.chosen()), (False, True))

    def test_nothing_is_written_while_it_is_off(self):
        names = FakeNames()
        recording = NamesWhenWanted(titles(chosen=False), names)
        recording.record(window("0xa", "steam"), "Steam")
        self.assertEqual(names.recorded, {})

    def test_names_are_written_while_it_is_on(self):
        names = FakeNames()
        NamesWhenWanted(titles(installed=True), names).record(window("0xa", "steam"), "Steam")
        self.assertEqual(names.recorded, {"0xa": "Steam"})


if __name__ == "__main__":
    unittest.main()
