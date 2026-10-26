import unittest
from pathlib import Path

from tests.adapters.mocked_files import files_holding
from tests.examples.windows import window
from hiru_tsatsi.adapters.storage.window_name_files import WindowNameFiles

FOLDER = Path("/home/sam/.local/state/window-names")


class NamingWindowsForTitleBars(unittest.TestCase):
    def test_one_file_per_window_holding_the_app_name(self):
        files = files_holding({})
        WindowNameFiles(FOLDER, files).record(window("0x55d1a2b3c4d0", "jetbrains-rider", "harbour – x"), "Rider Main")
        files.write.assert_called_once_with(FOLDER / "0x55d1a2b3c4d0", "Rider Main\n")

    def test_anything_but_a_window_address_is_never_written(self):
        for address in ["../escape", "..", ".", "0xg1", ""]:
            with self.subTest(address=address):
                files = files_holding({})
                WindowNameFiles(FOLDER, files).record(window(address, "x"), "Nope")
                files.write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
