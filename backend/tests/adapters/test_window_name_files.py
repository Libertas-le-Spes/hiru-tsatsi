import tempfile
import unittest
from pathlib import Path

from tests.fakes import window
from hiru_tsatsi.adapters.storage.window_name_files import WindowNameFiles


class NamingWindowsForTitleBars(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp()) / "window-names"
        self.names = WindowNameFiles(self.folder)

    def test_one_file_per_window_holding_the_app_name(self):
        self.names.record(window("0x55d1a2b3c4d0", "jetbrains-rider", "harbour – x"), "Rider Main")
        self.assertEqual((self.folder / "0x55d1a2b3c4d0").read_text(), "Rider Main\n")
        self.assertEqual([p.name for p in self.folder.iterdir()], ["0x55d1a2b3c4d0"])

    def test_a_later_run_replaces_the_name(self):
        self.names.record(window("0xa", "steam"), "Steam")
        self.names.record(window("0xa", "steam"), "Games")
        self.assertEqual((self.folder / "0xa").read_text(), "Games\n")

    def test_an_address_that_could_leave_the_folder_is_ignored(self):
        self.names.record(window("../escape", "x"), "Nope")
        self.assertFalse((self.folder.parent / "escape").exists())


if __name__ == "__main__":
    unittest.main()
