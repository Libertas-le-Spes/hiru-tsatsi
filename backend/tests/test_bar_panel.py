import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
TEXT_ITEM = re.compile(r"^[ \t]*Text[ \t]*\{", re.MULTILINE)


def block_after(source: str, start: int) -> str:
    depth = 0
    for position in range(source.index("{", start), len(source)):
        depth += {"{": 1, "}": -1}.get(source[position], 0)
        if depth == 0:
            return source[start:position + 1]
    return source[start:]


class TheBarPanel(unittest.TestCase):
    def test_every_text_shows_plain_text_so_a_window_title_cannot_carry_html(self):
        rich = [f"{path.name}:{source.count(chr(10), 0, found.start()) + 1}"
                for path in sorted(PLUGIN.glob("*.qml"))
                for source in [path.read_text()]
                for found in TEXT_ITEM.finditer(source)
                if "textFormat: Text.PlainText" not in block_after(source, found.start())]
        self.assertEqual(rich, [])


if __name__ == "__main__":
    unittest.main()
