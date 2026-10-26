import shlex
import subprocess
import unittest

from hiru_tsatsi.adapters.terminal import in_terminal


def script_of(command: str) -> str:
    return shlex.split(in_terminal(command, "hiru-tsatsi.2-0-helper"))[-1]


def run_as_the_terminal_would(command: str) -> str:
    done = subprocess.run(["sh", "-c", script_of(command)], input="\n", capture_output=True, text=True, timeout=10)
    return done.stdout


class OpeningACommandInATerminal(unittest.TestCase):
    def test_the_terminal_gets_the_apps_window_name_and_runs_the_command_through_sh(self):
        words = shlex.split(in_terminal("cd code && helper", "hiru-tsatsi.2-0-helper"))
        self.assertEqual(words[:5], ["xdg-terminal-exec", "--app-id=hiru-tsatsi.2-0-helper", "--", "sh", "-c"])
        self.assertTrue(words[5].startswith("(\ncd code && helper\n)\n"))

    def test_a_command_with_quotes_reaches_sh_unchanged(self):
        self.assertIn("""\necho "it's" '$HOME'\n""", script_of("""echo "it's" '$HOME'"""))

    def test_a_failing_command_keeps_the_terminal_open_and_says_why(self):
        self.assertIn("Stopped with exit code 3", run_as_the_terminal_would("exit 3"))

    def test_a_command_ending_in_a_comment_still_keeps_a_failure_open(self):
        self.assertIn("Stopped with exit code 1", run_as_the_terminal_would("false  # just a note"))

    def test_a_command_that_ends_well_closes_without_a_message(self):
        self.assertEqual(run_as_the_terminal_would("true"), "")


if __name__ == "__main__":
    unittest.main()
