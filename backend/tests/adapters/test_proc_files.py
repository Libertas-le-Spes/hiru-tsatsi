import unittest

from hiru_tsatsi.adapters.proc_files import TICKS_PER_SECOND, foreground_group_in, started_in


class ReadingWhichProcessIsInFront(unittest.TestCase):
    def test_the_eighth_field_of_a_status_line(self):
        self.assertEqual(foreground_group_in("31 (bash) S 30 31 31 34816 4242 4194304"), 4242)

    def test_a_program_name_with_spaces_and_brackets_does_not_shift_the_fields(self):
        self.assertEqual(foreground_group_in("31 (my (odd) tool) S 30 31 31 34816 4242 4194304"), 4242)

    def test_an_unreadable_status_line_means_none(self):
        self.assertEqual(foreground_group_in(""), 0)

class ReadingWhenAProcessStarted(unittest.TestCase):
    def test_the_twenty_second_field_in_seconds_since_boot(self):
        stat = "31 (bash) S 30 31 31 34816 4242 4194304 0 0 0 0 0 0 0 0 20 0 1 0 1700 0 0"
        self.assertEqual(started_in(stat), 1700 / TICKS_PER_SECOND)


if __name__ == "__main__":
    unittest.main()
