import unittest
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[2] / "bin" / "hiru-tsatsi"


class TheLauncher(unittest.TestCase):
    def test_starts_python_without_the_current_folder_on_its_import_path(self):
        self.assertIn('exec python3 -P -m hiru_tsatsi "$@"', LAUNCHER.read_text())


if __name__ == "__main__":
    unittest.main()
