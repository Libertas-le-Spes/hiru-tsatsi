import unittest
from unittest import mock

from hiru_tsatsi.adapters.proc_files import (TICKS_PER_SECOND, ProcFiles, foreground_group_in, process_group_in,
                                             real_user_in, started_in)


class ReadingWhichProcessIsInFront(unittest.TestCase):
    def test_the_eighth_field_of_a_status_line(self):
        self.assertEqual(foreground_group_in("31 (bash) S 30 31 31 34816 4242 4194304"), 4242)

    def test_a_program_name_with_spaces_and_brackets_does_not_shift_the_fields(self):
        self.assertEqual(foreground_group_in("31 (my (odd) tool) S 30 31 31 34816 4242 4194304"), 4242)

    def test_an_unreadable_status_line_means_none(self):
        self.assertEqual(foreground_group_in(""), 0)

    def test_the_fifth_field_is_the_group_the_process_belongs_to(self):
        self.assertEqual(process_group_in("62 (helper) S 61 62 31 34816 31 4194304"), 62)


class ReadingWhenAProcessStarted(unittest.TestCase):
    def test_the_twenty_second_field_in_seconds_since_boot(self):
        stat = "31 (bash) S 30 31 31 34816 4242 4194304 0 0 0 0 0 0 0 0 20 0 1 0 1700 0 0"
        self.assertEqual(started_in(stat), 1700 / TICKS_PER_SECOND)

STATUS = "Name:\thelper\nUid:\t1000\t1000\t1000\t1000\nGid:\t1000\t1000\t1000\t1000\n"


def proc_with(entries: dict[str, mock.MagicMock]) -> mock.MagicMock:
    root = mock.MagicMock(name="proc")
    listed = []
    for name, entry in entries.items():
        entry.name = name
        listed.append(entry)
    root.iterdir.return_value = listed
    return root


def a_process(status: str) -> mock.MagicMock:
    entry = mock.MagicMock()
    entry.__truediv__.return_value.read_text.return_value = status
    return entry


class ReadingProcessFiles(unittest.TestCase):
    def test_the_real_user_is_the_first_number_on_the_uid_line(self):
        self.assertEqual(real_user_in(STATUS), 1000)

    def test_own_processes_are_chosen_by_their_real_user(self):
        root = proc_with({"100": a_process(STATUS), "200": a_process(STATUS.replace("1000", "1001")),
                          "self": a_process(STATUS)})
        self.assertEqual(ProcFiles(root).own_pids(1000), [100])

    def test_a_process_that_is_gone_carries_nothing(self):
        root = mock.MagicMock()
        root.__truediv__.return_value.__truediv__.return_value.read_bytes.side_effect = FileNotFoundError()
        self.assertEqual(ProcFiles(root).environment(100), [])

    def test_a_process_whose_environment_is_hidden_cannot_be_told(self):
        root = mock.MagicMock()
        root.__truediv__.return_value.__truediv__.return_value.read_bytes.side_effect = PermissionError()
        self.assertIsNone(ProcFiles(root).environment(100))


if __name__ == "__main__":
    unittest.main()
