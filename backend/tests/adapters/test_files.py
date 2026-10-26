import unittest
from pathlib import Path
from unittest import mock

from hiru_tsatsi.adapters.storage import files
from hiru_tsatsi.adapters.storage.files import Disk
from hiru_tsatsi.use_cases.failures import NotReadable

LIST = Path("/home/sam/.config/hiru-tsatsi/apps.json")


def a_file_that_raises(error: Exception) -> mock.MagicMock:
    path = mock.MagicMock(name="path")
    path.read_text.side_effect = error
    return path


class ReadingAndWritingThroughTheDisk(unittest.TestCase):
    def test_a_missing_file_reads_as_nothing(self):
        self.assertEqual(Disk().read(a_file_that_raises(FileNotFoundError())), "")

    def test_a_file_that_exists_but_cannot_be_read_is_refused(self):
        with self.assertRaises(NotReadable):
            Disk().read(a_file_that_raises(PermissionError("denied")))

    def test_writes_once_through_the_safe_writer_passing_every_choice_on(self):
        with mock.patch.object(files, "write_atomically") as write_atomically:
            Disk().write(LIST, "text\n", read_before="before\n", follow_link=True)
        write_atomically.assert_called_once_with(LIST, "text\n", "before\n", True)


if __name__ == "__main__":
    unittest.main()
