import shlex
import unittest

from hiru_tsatsi.adapters.terminal import KEEP_OPEN_AFTER_FAILURE, XdgTerminal

WINDOW = "hiru-tsatsi.helper-1a2b3c4d"


def words(command: str) -> list[str]:
    return shlex.split(XdgTerminal().command_for(command, WINDOW))


class OpeningACommandInATerminal(unittest.TestCase):
    def test_runs_the_command_in_a_window_of_its_own_name_and_keeps_a_failure_on_screen(self):
        expected = ["xdg-terminal-exec", f"--app-id={WINDOW}", "--", "sh", "-c",
                    f"(\ncd code && helper\n)\n{KEEP_OPEN_AFTER_FAILURE}"]
        self.assertEqual(words("cd code && helper"), expected)


if __name__ == "__main__":
    unittest.main()
