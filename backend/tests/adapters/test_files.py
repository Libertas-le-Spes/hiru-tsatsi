import unittest
from pathlib import Path
from unittest import mock

from hiru_tsatsi.adapters.storage import files
from hiru_tsatsi.adapters.storage.atomic_file import NotWritten
from hiru_tsatsi.adapters.storage.files import Disk
from hiru_tsatsi.use_cases.ports import NotSaved

LIST = Path("/home/sam/.config/hiru-tsatsi/apps.json")


class WritingThroughTheDisk(unittest.TestCase):
    def test_writes_once_through_the_safe_writer(self):
        with mock.patch.object(files, "write_atomically") as write_atomically:
            Disk().write(LIST, "text\n", read_before="before\n")
        write_atomically.assert_called_once_with(LIST, "text\n", "before\n")

    def test_a_refused_write_is_reported_as_not_saved_with_its_reason(self):
        with mock.patch.object(files, "write_atomically", side_effect=NotWritten("folder belongs to another account")):
            with self.assertRaises(NotSaved) as refused:
                Disk().write(LIST, "text\n")
        self.assertEqual(str(refused.exception), "folder belongs to another account")


if __name__ == "__main__":
    unittest.main()
