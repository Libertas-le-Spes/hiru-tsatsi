import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from hiru_tsatsi.adapters.storage.atomic_file import NotWritten, write_atomically


class WritingAFileAtomically(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.file = self.folder / "example.conf"

    def test_a_write_that_fails_half_way_leaves_the_original_and_no_leftovers(self):
        self.file.write_text("original\n")
        with mock.patch("os.fsync", side_effect=OSError("power cut")), self.assertRaises(OSError):
            write_atomically(self.file, "replacement\n")
        self.assertEqual(self.file.read_text(), "original\n")
        self.assertEqual([path.name for path in self.folder.iterdir()], ["example.conf"])

    def test_a_linked_file_stays_a_link_and_its_target_gets_the_text(self):
        kept = self.folder / "dotfiles" / "example.conf"
        kept.parent.mkdir()
        kept.write_text("original\n")
        self.file.symlink_to(kept)
        write_atomically(self.file, "replacement\n")
        self.assertTrue(self.file.is_symlink())
        self.assertEqual(kept.read_text(), "replacement\n")

    def test_keeps_the_files_permissions(self):
        self.file.write_text("original\n")
        self.file.chmod(0o640)
        write_atomically(self.file, "replacement\n")
        self.assertEqual(stat.S_IMODE(self.file.stat().st_mode), 0o640)

    def test_a_new_file_is_readable_by_its_owner_only(self):
        write_atomically(self.file, "new\n")
        self.assertEqual(stat.S_IMODE(self.file.stat().st_mode), 0o600)

    def test_refuses_when_the_file_changed_since_it_was_read(self):
        self.file.write_text("edited by hand meanwhile\n")
        with self.assertRaises(NotWritten):
            write_atomically(self.file, "replacement\n", read_before="original\n")
        self.assertEqual(self.file.read_text(), "edited by hand meanwhile\n")

    def test_refuses_a_folder_that_belongs_to_another_account(self):
        with self.assertRaises(NotWritten):
            write_atomically(self.file, "new\n", account=lambda: os.getuid() + 1)
        self.assertFalse(self.file.exists())


if __name__ == "__main__":
    unittest.main()
