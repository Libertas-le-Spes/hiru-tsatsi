import unittest
from unittest import mock

from hiru_tsatsi.adapters.storage import atomic_file
from hiru_tsatsi.adapters.storage.atomic_file import write_atomically
from hiru_tsatsi.use_cases.ports import NotSaved

OWNER = 1000
KEPT_MODE = 0o100640
OWNERS_FOLDER = 0o40755
SHARED_FOLDER = 0o40777


def owner() -> int:
    return OWNER


def another_account() -> int:
    return OWNER + 1


class AFileOnDisk:
    def __init__(self, exists: bool = True, text: str = "original\n"):
        self.path = mock.MagicMock(name="path")
        self.target = self.path
        self.folder = self.target.parent
        self.link_folder = self.path.parent
        for folder in (self.folder, self.link_folder):
            folder.stat.return_value.st_uid = OWNER
            folder.stat.return_value.st_mode = OWNERS_FOLDER
        self.target.exists.return_value = exists
        self.target.stat.return_value.st_mode = KEPT_MODE
        self.target.read_text.return_value = text


class WritingAFileAtomically(unittest.TestCase):
    def setUp(self):
        self.os = mock.patch.object(atomic_file, "os").start()
        self.tempfile = mock.patch.object(atomic_file, "tempfile").start()
        self.copy_path = mock.patch.object(atomic_file, "Path").start()
        self.tempfile.mkstemp.return_value = (7, "/home/sam/.config/.example.conf-x1")
        self.addCleanup(mock.patch.stopall)

    def copy(self):
        return self.copy_path.return_value

    def test_writes_a_new_copy_beside_the_real_file_and_swaps_it_in_once(self):
        disk = AFileOnDisk()
        write_atomically(disk.path, "replacement\n", account=owner)
        self.tempfile.mkstemp.assert_called_once_with(dir=disk.folder, prefix=f".{disk.target.name}-")
        self.os.fdopen.return_value.__enter__.return_value.write.assert_called_once_with("replacement\n")
        self.os.replace.assert_called_once_with(self.copy(), disk.target)

    def test_by_default_replaces_a_link_instead_of_following_it(self):
        disk = AFileOnDisk()
        write_atomically(disk.path, "replacement\n", account=owner)
        disk.path.resolve.assert_not_called()
        self.os.replace.assert_called_once_with(self.copy(), disk.path)

    def test_follows_a_link_only_when_asked_so_a_linked_dotfile_stays_a_link(self):
        disk = AFileOnDisk()
        resolved = disk.path.resolve.return_value
        resolved.parent.stat.return_value.st_uid = OWNER
        resolved.parent.stat.return_value.st_mode = OWNERS_FOLDER
        resolved.exists.return_value = False
        write_atomically(disk.path, "replacement\n", follow_link=True, account=owner)
        self.os.replace.assert_called_once_with(self.copy(), resolved)

    def test_refuses_a_folder_other_accounts_can_write_to(self):
        disk = AFileOnDisk()
        disk.folder.stat.return_value.st_mode = SHARED_FOLDER
        with self.assertRaises(NotSaved):
            write_atomically(disk.path, "replacement\n", account=owner)
        self.tempfile.mkstemp.assert_not_called()

    def test_refuses_to_follow_a_link_planted_in_a_folder_other_accounts_can_write_to(self):
        disk = AFileOnDisk()
        resolved = disk.path.resolve.return_value
        resolved.parent.stat.return_value.st_uid = OWNER
        resolved.parent.stat.return_value.st_mode = OWNERS_FOLDER
        disk.link_folder.stat.return_value.st_mode = SHARED_FOLDER
        with self.assertRaises(NotSaved):
            write_atomically(disk.path, "replacement\n", follow_link=True, account=owner)
        self.os.replace.assert_not_called()

    def test_keeps_the_permissions_of_the_file_it_replaces(self):
        disk = AFileOnDisk()
        write_atomically(disk.path, "replacement\n", account=owner)
        written = self.os.fdopen.return_value.__enter__.return_value
        self.os.fchmod.assert_called_once_with(written.fileno.return_value, 0o640)

    def test_a_new_file_is_for_its_owner_only(self):
        disk = AFileOnDisk(exists=False)
        write_atomically(disk.path, "new\n", account=owner)
        written = self.os.fdopen.return_value.__enter__.return_value
        self.os.fchmod.assert_called_once_with(written.fileno.return_value, 0o600)

    def test_flushes_the_copy_and_then_the_folder_to_disk(self):
        disk = AFileOnDisk()
        write_atomically(disk.path, "replacement\n", account=owner)
        self.assertEqual(self.os.fsync.call_count, 2)
        self.os.open.assert_called_once_with(disk.folder, self.os.O_RDONLY | self.os.O_DIRECTORY)
        self.os.close.assert_called_once_with(self.os.open.return_value)

    def test_refuses_when_the_file_changed_since_it_was_read_and_removes_the_copy(self):
        disk = AFileOnDisk(text="edited by hand meanwhile\n")
        with self.assertRaises(NotSaved):
            write_atomically(disk.path, "replacement\n", read_before="original\n", account=owner)
        self.os.replace.assert_not_called()
        self.copy().unlink.assert_called_once_with(missing_ok=True)

    def test_a_write_that_fails_half_way_never_swaps_and_removes_the_copy(self):
        disk = AFileOnDisk()
        self.os.fsync.side_effect = OSError("power cut")
        with self.assertRaises(OSError):
            write_atomically(disk.path, "replacement\n", account=owner)
        self.os.replace.assert_not_called()
        self.copy().unlink.assert_called_with(missing_ok=True)

    def test_refuses_a_folder_that_belongs_to_another_account_before_writing_anything(self):
        disk = AFileOnDisk()
        with self.assertRaises(NotSaved):
            write_atomically(disk.path, "new\n", account=another_account)
        self.tempfile.mkstemp.assert_not_called()
        self.os.replace.assert_not_called()


if __name__ == "__main__":
    unittest.main()
