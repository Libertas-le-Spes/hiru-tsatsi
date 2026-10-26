import unittest
from pathlib import Path
from unittest import mock

from hiru_tsatsi.adapters.proc_files import (TICKS_PER_SECOND, ProcFiles, foreground_group_in, process_group_in,
                                             real_user_in, started_in)

STATUS = "Name:\thelper\nUid:\t1000\t1000\t1000\t1000\nGid:\t1000\t1000\t1000\t1000\n"


def a_path() -> mock.Mock:
    return mock.create_autospec(Path, instance=True)


def a_file(content: str) -> mock.Mock:
    file = a_path()
    file.read_text.return_value = content
    return file


def an_unreadable_file(error: OSError) -> mock.Mock:
    file = a_path()
    file.read_text.side_effect = error
    file.read_bytes.side_effect = error
    file.readlink.side_effect = error
    return file


def a_folder(name: str, files: dict[str, mock.Mock]) -> mock.Mock:
    folder = a_path()
    folder.name = name

    def inside(part: str) -> mock.Mock:
        return files.get(part, an_unreadable_file(FileNotFoundError()))

    folder.__truediv__.side_effect = inside
    return folder


def proc_with(processes: dict[str, mock.Mock], files: dict[str, mock.Mock]) -> mock.Mock:
    everything = dict(processes)
    everything.update(files)
    root = a_folder("proc", everything)
    root.iterdir.return_value = list(processes.values())
    return root


def a_process(pid: str, files: dict[str, mock.Mock]) -> mock.Mock:
    return a_folder(pid, files)


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

class ReadingProcessFiles(unittest.TestCase):
    def test_the_real_user_is_the_first_number_on_the_uid_line(self):
        self.assertEqual(real_user_in(STATUS), 1000)

    def test_own_processes_are_chosen_by_their_real_user(self):
        root = proc_with({"100": a_process("100", {"status": a_file(STATUS)}),
                          "200": a_process("200", {"status": a_file(STATUS.replace("1000", "1001"))}),
                          "self": a_process("self", {"status": a_file(STATUS)})}, {})
        self.assertEqual(ProcFiles(root).own_pids(1000), [100])

    def test_processes_that_cannot_be_listed_are_unknown(self):
        root = proc_with({}, {})
        root.iterdir.side_effect = PermissionError()
        self.assertIsNone(ProcFiles(root).own_pids(1000))

    def test_a_process_that_is_gone_carries_nothing(self):
        root = proc_with({"100": a_process("100", {"environ": an_unreadable_file(FileNotFoundError())})}, {})
        self.assertEqual(ProcFiles(root).environment(100), [])

    def test_a_process_whose_environment_is_hidden_cannot_be_told(self):
        root = proc_with({"100": a_process("100", {"environ": an_unreadable_file(PermissionError())})}, {})
        self.assertIsNone(ProcFiles(root).environment(100))

    def test_a_process_whose_start_cannot_be_read_has_no_start(self):
        root = proc_with({"100": a_process("100", {"stat": an_unreadable_file(PermissionError())})}, {})
        self.assertIsNone(ProcFiles(root).started(100))

    def test_the_time_since_boot_is_the_first_number_of_uptime(self):
        root = proc_with({}, {"uptime": a_file("1234.5 9876.0\n")})
        self.assertEqual(ProcFiles(root).seconds_since_boot(), 1234.5)

    def test_a_time_since_boot_that_cannot_be_read_is_unknown(self):
        root = proc_with({}, {"uptime": an_unreadable_file(PermissionError())})
        self.assertIsNone(ProcFiles(root).seconds_since_boot())

    def test_the_children_are_the_numbers_listed_for_its_main_thread(self):
        root = proc_with({"100": a_process("100", {"task/100/children": a_file("101 102 ")})}, {})
        self.assertEqual(ProcFiles(root).children(100), [101, 102])

    def test_a_folder_that_cannot_be_read_is_empty(self):
        root = proc_with({"100": a_process("100", {"cwd": an_unreadable_file(PermissionError())})}, {})
        self.assertEqual(ProcFiles(root).folder(100), "")


if __name__ == "__main__":
    unittest.main()
