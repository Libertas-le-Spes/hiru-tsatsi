import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
TEXT_ITEM = re.compile(r"^[ \t]*Text[ \t]*\{", re.MULTILINE)
PLAIN = "textFormat: Text.PlainText"


def block_starting_at(source: str, start: int) -> str:
    depth = 0
    for position in range(source.index("{", start), len(source)):
        if source[position] == "{":
            depth += 1
        if source[position] == "}":
            depth -= 1
        if depth == 0:
            return source[start:position + 1]
    return source[start:]


def line_number(source: str, position: int) -> int:
    return source.count("\n", 0, position) + 1


def text_items_that_may_show_rich_text(path: Path) -> list[str]:
    source = path.read_text()
    rich = []
    for found in TEXT_ITEM.finditer(source):
        if PLAIN not in block_starting_at(source, found.start()):
            rich.append(f"{path.name}:{line_number(source, found.start())}")
    return rich


class TheBarPanel(unittest.TestCase):
    def test_every_text_shows_plain_text_so_a_window_title_cannot_carry_html(self):
        rich = []
        for path in sorted(PLUGIN.glob("*.qml")):
            rich += text_items_that_may_show_rich_text(path)
        self.assertEqual(rich, [])


if __name__ == "__main__":
    unittest.main()
