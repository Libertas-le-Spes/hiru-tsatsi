import re
import unittest
from pathlib import Path

from hiru_tsatsi.entrypoints.cli.command_list import COMMANDS

PANEL = Path(__file__).resolve().parents[2] / "Panel.qml"
CHANGE = re.compile(r'root\.change\(\["([a-z-]+)"')
RUN = re.compile(r'\[root\.hiruTsatsiCommand, "([a-z-]+)"')


def commands_the_panel_sends() -> set[str]:
    source = PANEL.read_text()
    sent = set()
    for pattern in (CHANGE, RUN):
        for found in pattern.finditer(source):
            sent.add(found.group(1))
    return sent


class TheBarPanelAndTheCommandLine(unittest.TestCase):
    def test_the_panel_sends_commands(self):
        self.assertGreaterEqual(len(commands_the_panel_sends()), 6)

    def test_every_command_the_panel_sends_exists(self):
        unknown = []
        for command in sorted(commands_the_panel_sends()):
            if command not in COMMANDS:
                unknown.append(command)
        self.assertEqual(unknown, [])


if __name__ == "__main__":
    unittest.main()
