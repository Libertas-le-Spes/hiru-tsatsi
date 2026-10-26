import re
import unittest
from pathlib import Path

from hiru_tsatsi.entrypoints.cli.command_list import COMMANDS
from hiru_tsatsi.entrypoints.cli.main import parser

PANEL = Path(__file__).resolve().parents[2] / "Panel.qml"
CHANGE = re.compile(r'root\.change\(\["([a-z-]+)"((?:, [^,\]]+)*)\]\)')
RUN = re.compile(r'\[root\.hiruTsatsiCommand, "([a-z-]+)"((?:, [^,\]]+)*)\]')
EDITS_ARE_SENT_AFTER = "--"


def calls(pattern: re.Pattern) -> list[tuple[str, int]]:
    found = []
    for call in pattern.finditer(PANEL.read_text()):
        arguments = call.group(2).count(",")
        found.append((call.group(1), arguments))
    return found


def as_typed(command: str, arguments: int, edit: bool) -> list[str]:
    typed = [command]
    if edit:
        typed.append(EDITS_ARE_SENT_AFTER)
    for _ in range(arguments):
        typed.append("1")
    return typed


class TheBarPanelAndTheCommandLine(unittest.TestCase):
    def test_the_panel_sends_commands(self):
        self.assertGreaterEqual(len(calls(CHANGE)) + len(calls(RUN)), 6)

    def test_every_command_the_panel_sends_exists(self):
        unknown = []
        for command, _ in calls(CHANGE) + calls(RUN):
            if command not in COMMANDS:
                unknown.append(command)
        self.assertEqual(unknown, [])

    def test_every_edit_the_panel_sends_is_read_with_the_right_number_of_arguments(self):
        for command, arguments in calls(CHANGE):
            with self.subTest(command=command):
                parser().parse_args(as_typed(command, arguments, edit=True))

    def test_every_other_command_the_panel_runs_is_read_with_the_right_number_of_arguments(self):
        for command, arguments in calls(RUN):
            with self.subTest(command=command):
                parser().parse_args(as_typed(command, arguments, edit=False))

    def test_the_panel_sends_every_edit_after_the_mark_that_ends_options(self):
        self.assertIn(f'[root.hiruTsatsiCommand, edit[0], "{EDITS_ARE_SENT_AFTER}"]', PANEL.read_text())


if __name__ == "__main__":
    unittest.main()
