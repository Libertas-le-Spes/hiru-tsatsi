import os
import subprocess
import tempfile
import unittest
from pathlib import Path

INSTALL = Path(__file__).resolve().parents[2] / "install.sh"


def install(home: Path) -> subprocess.CompletedProcess:
    env = {"HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config"), "XDG_STATE_HOME": str(home / ".local/state"),
           "PATH": os.environ["PATH"]}
    return subprocess.run(["sh", str(INSTALL)], env=env, capture_output=True, text=True, timeout=30)


class TheInstaller(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.bin = self.home / ".local" / "bin"
        self.bin.mkdir(parents=True)

    def test_leaves_another_tool_called_tsatsi_alone(self):
        (self.bin / "tsatsi").write_text("#!/bin/sh\necho another tool\n")
        done = install(self.home)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("is not Hiru Tsatsi", done.stderr)
        self.assertEqual((self.bin / "tsatsi").read_text(), "#!/bin/sh\necho another tool\n")
        self.assertFalse((self.bin / "hiru-tsatsi").exists())

    def test_links_both_commands_when_they_are_free(self):
        install(self.home)
        for name in ("tsatsi", "hiru-tsatsi"):
            self.assertEqual(os.readlink(self.bin / name), str(INSTALL.parent / "backend" / "bin" / "hiru-tsatsi"))

    def test_replaces_a_link_to_an_earlier_hiru_tsatsi_install(self):
        (self.bin / "tsatsi").symlink_to("/elsewhere/hiru-tsatsi/backend/bin/hiru-tsatsi")
        install(self.home)
        self.assertEqual(os.readlink(self.bin / "tsatsi"), str(INSTALL.parent / "backend" / "bin" / "hiru-tsatsi"))

    def test_removes_the_old_short_name_when_it_is_hiru_tsatsi(self):
        (self.bin / "hiru").symlink_to("/elsewhere/hiru-tsatsi/backend/bin/hiru-tsatsi")
        install(self.home)
        self.assertFalse((self.bin / "hiru").is_symlink())

    def test_keeps_another_tool_that_is_called_hiru(self):
        (self.bin / "hiru").write_text("#!/bin/sh\necho another tool\n")
        install(self.home)
        self.assertEqual((self.bin / "hiru").read_text(), "#!/bin/sh\necho another tool\n")


if __name__ == "__main__":
    unittest.main()
