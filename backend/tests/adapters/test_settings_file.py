import unittest
from pathlib import Path

from tests.adapters.mocked_files import files_holding
from hiru_tsatsi.adapters.storage.settings_file import SettingsFile

SETTINGS = Path("/home/sam/.config/hiru-tsatsi/settings.json")


class KeepingSettings(unittest.TestCase):
    def test_nothing_chosen_while_no_settings_are_saved(self):
        self.assertIsNone(SettingsFile(SETTINGS, files_holding({})).window_titles())

    def test_a_saved_choice_is_read(self):
        self.assertIs(SettingsFile(SETTINGS, files_holding({SETTINGS: '{"window_titles": false}'})).window_titles(), False)

    def test_a_choice_is_written_once_keeping_the_other_settings(self):
        files = files_holding({SETTINGS: '{"theme": "dark"}'})
        SettingsFile(SETTINGS, files).set_window_titles(True)
        files.write.assert_called_once_with(SETTINGS, '{\n  "theme": "dark",\n  "window_titles": true\n}\n')

    def test_an_unreadable_file_means_nothing_chosen(self):
        self.assertIsNone(SettingsFile(SETTINGS, files_holding({SETTINGS: "not json"})).window_titles())

    def test_a_value_that_is_not_yes_or_no_means_nothing_chosen(self):
        self.assertIsNone(SettingsFile(SETTINGS, files_holding({SETTINGS: '{"window_titles": "yes"}'})).window_titles())


if __name__ == "__main__":
    unittest.main()
