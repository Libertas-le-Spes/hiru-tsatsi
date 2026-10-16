import tempfile
import unittest
from pathlib import Path

from hiru_tsatsi.adapters.storage.settings_file import SettingsFile


class KeepingSettings(unittest.TestCase):
    def test_nothing_chosen_until_a_choice_is_saved(self):
        settings = SettingsFile(Path(tempfile.mkdtemp()) / "hiru-tsatsi" / "settings.json")
        self.assertIsNone(settings.window_titles())
        settings.set_window_titles(False)
        self.assertIs(SettingsFile(settings.path).window_titles(), False)

    def test_an_unreadable_file_means_nothing_chosen(self):
        path = Path(tempfile.mkdtemp()) / "settings.json"
        path.write_text("not json")
        self.assertIsNone(SettingsFile(path).window_titles())


if __name__ == "__main__":
    unittest.main()
