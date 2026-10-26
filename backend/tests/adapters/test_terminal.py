import shlex
import unittest

from hiru_tsatsi.adapters.terminal import KEEP_OPEN_AFTER_FAILURE, XdgTerminal

WINDOW = "hiru-tsatsi.helper-1a2b3c4d"


def words(command: str) -> list[str]:
    return shlex.split(XdgTerminal().command_for(command, WINDOW))


class OpeningACommandInATerminal(unittest.TestCase):
    def test_asks_the_terminal_for_a_window_with_the_apps_own_name_running_sh(self):
        self.assertEqual(words("cd code && helper")[:5], ["xdg-terminal-exec", f"--app-id={WINDOW}", "--", "sh", "-c"])

    def test_runs_the_command_in_its_own_shell_then_keeps_a_failure_on_screen(self):
        self.assertEqual(words("cd code && helper")[5], f"(\ncd code && helper\n)\n{KEEP_OPEN_AFTER_FAILURE}")


if __name__ == "__main__":
    unittest.main()
