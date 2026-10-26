import unittest

from tests.fakes import HOME, window
from hiru_tsatsi.work_apps.inside import Inside, window_running


class ReadingWhatACommandRunsAndWhere(unittest.TestCase):
    def test_a_command_that_goes_to_a_folder_and_runs_a_program(self):
        cases = {
            "cd code/harbour && helper": Inside("/home/sam/code/harbour", "helper"),
            "cd ~/code/lantern; nvim notes.md": Inside("/home/sam/code/lantern", "nvim"),
            "cd /srv/site && /usr/bin/helper --resume": Inside("/srv/site", "helper"),
            "cd 'my code' && helper": Inside("/home/sam/my code", "helper"),
            "cd ~ && helper": Inside("/home/sam", "helper"),
            "cd code/../code/tide/ && helper": Inside("/home/sam/code/tide", "helper"),
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(Inside.of(command, HOME), expected)

    def test_other_commands_say_nothing_about_what_runs_inside(self):
        for command in ["helper", "omarchy-launch-webapp https://example.com/", "cd code", "cd code || helper",
                        "cd 'unclosed && helper", "(cd code && helper)"]:
            with self.subTest(command=command):
                self.assertIsNone(Inside.of(command, HOME))


class FindingTheWindowARunningProgramIsIn(unittest.TestCase):
    def setUp(self):
        self.windows = [window("a", "foot", "✳ Some talk", 3, "helper", "/home/sam/code/lantern"),
                        window("b", "foot", "✳ Other talk", 2, "helper", "/home/sam/code/harbour")]

    def test_the_window_with_that_program_in_that_folder_whatever_its_title(self):
        self.assertEqual(window_running("cd code/harbour && helper", HOME, self.windows, set()).address, "b")

    def test_a_claimed_window_is_not_taken_twice(self):
        self.assertIsNone(window_running("cd code/harbour && helper", HOME, self.windows, {"b"}))

    def test_the_same_program_in_another_folder_is_not_it(self):
        self.assertIsNone(window_running("cd code/tide && helper", HOME, self.windows, set()))


if __name__ == "__main__":
    unittest.main()
