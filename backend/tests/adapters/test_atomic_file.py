import unittest
from unittest import mock

from hiru_tsatsi.adapters.storage import atomic_file
from hiru_tsatsi.adapters.storage.atomic_file import write_atomically
from hiru_tsatsi.use_cases.failures import NotSaved

OWNER = 1000
KEPT_MODE = 0o100640
OWNERS_FOLDER = 0o40755
SHARED_FOLDER = 0o40777


def owner() -> int:
    return OWNER


def another_account() -> int:
    return OWNER + 1


def a_folder(mode: int = OWNERS_FOLDER, exists: bool = True) -> mock.MagicMock:
    folder = mock.MagicMock(name="folder")
    folder.stat.return_value.st_uid = OWNER
    folder.stat.return_value.st_mode = mode
    folder.exists.return_value = exists
    return folder


def a_file(folder: mock.MagicMock, exists: bool = True, text: str = "original\n") -> mock.MagicMock:
    file = mock.MagicMock(name="file")
    file.parent = folder
    file.is_symlink.return_value = False
    file.exists.return_value = exists
    file.stat.return_value.st_mode = KEPT_MODE
    file.read_text.return_value = text
    return file


def a_link(folder: mock.MagicMock, next_hop: mock.MagicMock, resolved: mock.MagicMock) -> mock.MagicMock:
    link = a_file(folder)
    link.is_symlink.return_value = True
    folder.__truediv__.return_value = next_hop
    link.resolve.return_value = resolved
    return link


class WritingAFileAtomically(unittest.TestCase):
    def setUp(self):
        self.os = mock.patch.object(atomic_file, "os").start()
        self.tempfile = mock.patch.object(atomic_file, "tempfile").start()
        self.copy_path = mock.patch.object(atomic_file, "Path").start()
        self.tempfile.mkstemp.return_value = (7, "/home/sam/.config/.example.conf-x1")
        self.addCleanup(mock.patch.stopall)

    def copy(self):
        return self.copy_path.return_value

    def written(self):
        return self.os.fdopen.return_value.__enter__.return_value

    def test_writes_a_new_copy_beside_the_real_file_and_swaps_it_in_once(self):
        file = a_file(a_folder())
        write_atomically(file, "replacement\n", account=owner)
        self.tempfile.mkstemp.assert_called_once_with(dir=file.parent, prefix=f".{file.name}-")
        self.written().write.assert_called_once_with("replacement\n")
        self.os.replace.assert_called_once_with(self.copy(), file)

    def test_refuses_a_link_unless_asked_to_follow_it_and_never_replaces_it(self):
        link = a_link(a_folder(), a_file(a_folder()), a_file(a_folder()))
        with self.assertRaises(NotSaved):
            write_atomically(link, "replacement\n", account=owner)
        link.resolve.assert_not_called()
        self.tempfile.mkstemp.assert_not_called()
        self.os.replace.assert_not_called()

    def test_follows_a_link_when_asked_so_a_linked_dotfile_stays_a_link(self):
        real = a_file(a_folder(), exists=False)
        link = a_link(a_folder(), a_file(a_folder()), real)
        write_atomically(link, "replacement\n", follow_link=True, account=owner)
        self.os.replace.assert_called_once_with(self.copy(), real)

    def test_refuses_to_follow_a_link_planted_in_a_folder_other_accounts_can_write_to(self):
        link = a_link(a_folder(SHARED_FOLDER), a_file(a_folder()), a_file(a_folder()))
        with self.assertRaises(NotSaved):
            write_atomically(link, "replacement\n", follow_link=True, account=owner)
        self.os.replace.assert_not_called()

    def test_refuses_a_chain_of_links_that_passes_through_a_shared_folder(self):
        middle = a_link(a_folder(SHARED_FOLDER), a_file(a_folder()), a_file(a_folder()))
        first = a_link(a_folder(), middle, a_file(a_folder()))
        with self.assertRaises(NotSaved):
            write_atomically(first, "replacement\n", follow_link=True, account=owner)
        self.os.replace.assert_not_called()

    def test_refuses_a_folder_other_accounts_can_write_to(self):
        file = a_file(a_folder(SHARED_FOLDER))
        with self.assertRaises(NotSaved):
            write_atomically(file, "replacement\n", account=owner)
        self.tempfile.mkstemp.assert_not_called()

    def test_refuses_a_folder_that_belongs_to_another_account_before_writing_anything(self):
        file = a_file(a_folder())
        with self.assertRaises(NotSaved):
            write_atomically(file, "new\n", account=another_account)
        self.tempfile.mkstemp.assert_not_called()
        self.os.replace.assert_not_called()

    def test_creates_missing_folders_for_their_owner_only(self):
        missing = a_folder(exists=False)
        missing.parent = a_folder()
        write_atomically(a_file(missing, exists=False), "new\n", account=owner)
        missing.mkdir.assert_called_once_with(mode=0o700)

    def test_keeps_the_permissions_of_the_file_it_replaces(self):
        write_atomically(a_file(a_folder()), "replacement\n", account=owner)
        self.os.fchmod.assert_called_once_with(self.written().fileno.return_value, 0o640)

    def test_a_new_file_is_for_its_owner_only(self):
        write_atomically(a_file(a_folder(), exists=False), "new\n", account=owner)
        self.os.fchmod.assert_called_once_with(self.written().fileno.return_value, 0o600)

    def test_flushes_the_copy_and_then_the_folder_to_disk(self):
        file = a_file(a_folder())
        write_atomically(file, "replacement\n", account=owner)
        self.assertEqual(self.os.fsync.call_count, 2)
        self.os.open.assert_called_once_with(file.parent, self.os.O_RDONLY | self.os.O_DIRECTORY)
        self.os.close.assert_called_once_with(self.os.open.return_value)

    def test_refuses_when_the_file_changed_since_it_was_read_and_removes_the_copy(self):
        file = a_file(a_folder(), text="edited by hand meanwhile\n")
        with self.assertRaises(NotSaved):
            write_atomically(file, "replacement\n", read_before="original\n", account=owner)
        self.os.replace.assert_not_called()
        self.copy().unlink.assert_called_once_with(missing_ok=True)

    def test_a_write_that_fails_half_way_never_swaps_and_removes_the_copy(self):
        self.os.fsync.side_effect = OSError("power cut")
        with self.assertRaises(OSError):
            write_atomically(a_file(a_folder()), "replacement\n", account=owner)
        self.os.replace.assert_not_called()
        self.copy().unlink.assert_called_with(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
