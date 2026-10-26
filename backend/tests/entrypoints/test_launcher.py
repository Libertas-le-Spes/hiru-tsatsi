import subprocess
import tempfile
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[2] / "bin" / "hiru-tsatsi"


class TheLauncher(unittest.TestCase):
    def test_never_runs_python_files_from_the_folder_it_is_started_in(self):
        folder = Path(tempfile.mkdtemp())
        marker = folder / "planted-file-ran"
        (folder / "json.py").write_text(f"open({str(marker)!r}, 'w').close()\n")
        subprocess.run([str(LAUNCHER), "--help"], cwd=folder, capture_output=True, timeout=30)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
