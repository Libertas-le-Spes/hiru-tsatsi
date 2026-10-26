import unittest

from hiru_tsatsi.adapters.proc_files import foreground_group_in


class ReadingWhichProcessIsInFront(unittest.TestCase):
    def test_the_eighth_field_of_a_status_line(self):
        self.assertEqual(foreground_group_in("31 (bash) S 30 31 31 34816 4242 4194304"), 4242)

    def test_a_program_name_with_spaces_and_brackets_does_not_shift_the_fields(self):
        self.assertEqual(foreground_group_in("31 (my (odd) tool) S 30 31 31 34816 4242 4194304"), 4242)

    def test_an_unreadable_status_line_means_none(self):
        self.assertEqual(foreground_group_in(""), 0)


if __name__ == "__main__":
    unittest.main()
