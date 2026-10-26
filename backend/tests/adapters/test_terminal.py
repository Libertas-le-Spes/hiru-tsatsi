import shlex
import unittest

from hiru_tsatsi.adapters.terminal import KEEP_OPEN_AFTER_FAILURE, in_terminal

WINDOW = "hiru-tsatsi.2-0-helper"


def words(command: str) -> list[str]:
    return shlex.split(in_terminal(command, WINDOW))


class OpeningACommandInATerminal(unittest.TestCase):
    def test_asks_the_terminal_for_a_window_with_the_apps_own_name_running_sh(self):
        self.assertEqual(words("cd code && helper")[:5], ["xdg-terminal-exec", f"--app-id={WINDOW}", "--", "sh", "-c"])

    def test_runs_the_command_in_its_own_shell_then_keeps_a_failure_on_screen(self):
        self.assertEqual(words("cd code && helper")[5], f"(\ncd code && helper\n)\n{KEEP_OPEN_AFTER_FAILURE}")

    def test_a_command_with_quotes_reaches_sh_unchanged(self):
        command = """echo "it's" '$HOME'"""
        self.assertEqual(words(command)[5], f"(\n{command}\n)\n{KEEP_OPEN_AFTER_FAILURE}")


if __name__ == "__main__":
    unittest.main()
