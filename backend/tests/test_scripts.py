import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]
LAUNCHER = REPOSITORY / "backend" / "bin" / "hiru-tsatsi"
INSTALLER = REPOSITORY / "install.sh"


class TheShellScripts(unittest.TestCase):
    def test_the_launcher_starts_python_without_the_current_folder_on_its_import_path(self):
        self.assertIn('exec python3 -P -m hiru_tsatsi "$@"', LAUNCHER.read_text())

    def test_the_installer_runs_the_python_install_step_and_stops_if_it_fails(self):
        self.assertIn('python3 -P -m hiru_tsatsi.entrypoints.install "$bin_dir" "$here/backend/bin/hiru-tsatsi" || exit 1',
                      INSTALLER.read_text())


if __name__ == "__main__":
    unittest.main()
