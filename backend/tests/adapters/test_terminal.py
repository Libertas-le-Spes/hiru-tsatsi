import shlex
import unittest

from hiru_tsatsi.adapters.terminal import XdgTerminal

WINDOW = "hiru-tsatsi.helper-1a2b3c4d"
SCRIPT = """(
cd code && helper
)
status=$?
if [ "$status" -ne 0 ]; then
    printf '\\nStopped with exit code %s. Press Enter to close. ' "$status"
    read -r _
fi"""


def words(command: str) -> list[str]:
    return shlex.split(XdgTerminal().command_for(command, WINDOW))


class OpeningACommandInATerminal(unittest.TestCase):
    def test_runs_the_command_in_a_window_of_its_own_name_and_keeps_a_failure_on_screen(self):
        expected = ["xdg-terminal-exec", f"--app-id={WINDOW}", "--", "sh", "-c", SCRIPT]
        self.assertEqual(words("cd code && helper"), expected)


if __name__ == "__main__":
    unittest.main()
