import unittest

from tests.examples.windows import window
from tests.examples.home import HOME
from hiru_tsatsi.work_apps.program_in_folder import ProgramInFolder


class ReadingWhatACommandRunsAndWhere(unittest.TestCase):
    def test_a_command_that_goes_to_a_folder_and_runs_a_program(self):
        cases = {
            "cd code/harbour && helper": ProgramInFolder("helper", "/home/sam/code/harbour"),
            "cd ~/code/lantern; nvim notes.md": ProgramInFolder("nvim", "/home/sam/code/lantern"),
            "cd ~/code/tide&&helper": ProgramInFolder("helper", "/home/sam/code/tide"),
            "cd /srv/site && /usr/bin/helper --resume": ProgramInFolder("helper", "/srv/site"),
            "cd 'my code' && helper": ProgramInFolder("helper", "/home/sam/my code"),
            "cd ~ && helper": ProgramInFolder("helper", "/home/sam"),
            "cd code/../code/tide/ && helper": ProgramInFolder("helper", "/home/sam/code/tide"),
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(ProgramInFolder.of(command, HOME), expected)

    def test_other_commands_say_nothing_about_what_runs_inside(self):
        commands = ["helper", "omarchy-launch-webapp https://example.com/", "cd code", "cd code || helper",
                    "cd 'unclosed && helper", "(cd code && helper)", 'cd "$HOME/code" && helper',
                    "cd `pwd`/code && helper", "cd ~sam/code && helper", "cd code && env X=1 helper",
                    "cd code; exec helper", "cd code && nohup helper", "cd code && sudo helper",
                    "cd code && bash", "cd code && sh run.sh", "cd code && A=1 helper",
                    "cd code && npx helper", "cd code && systemd-run --user helper", "cd code && timeout 9 helper",
                    "cd code && uwsm app -- helper", "cd code && flatpak run org.example.Helper",
                    "cd code && $EDITOR", "cd code && `which helper`", "cd code && ( helper )",
                    "cd code && { helper; }", "cd code && *", "cd code && help*"]
        for command in commands:
            with self.subTest(command=command):
                self.assertIsNone(ProgramInFolder.of(command, HOME))


class TellingWhetherAWindowRunsIt(unittest.TestCase):
    def test_the_same_program_in_the_same_folder(self):
        helper = ProgramInFolder("helper", "/home/sam/code")
        self.assertTrue(helper.runs_in(window("a", "foot", "✳ Some talk", 2, "helper", "/home/sam/code")))

    def test_the_same_program_in_another_folder_or_another_program(self):
        helper = ProgramInFolder("helper", "/home/sam/code")
        self.assertFalse(helper.runs_in(window("a", "foot", "", 2, "helper", "/home/sam/other")))
        self.assertFalse(helper.runs_in(window("b", "foot", "", 2, "bash", "/home/sam/code")))


if __name__ == "__main__":
    unittest.main()
