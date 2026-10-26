import ast
import unittest
from pathlib import Path

PACKAGE = Path(__file__).parent.parent / "hiru_tsatsi"

MAY_IMPORT = {
    "work_apps": {"work_apps"},
    "use_cases": {"work_apps", "use_cases"},
    "presenters": {"work_apps", "use_cases", "presenters"},
    "adapters": {"work_apps", "use_cases", "adapters"},
    "entrypoints": {"work_apps", "use_cases", "presenters", "entrypoints", "wiring"},
    "wiring": {"work_apps", "use_cases", "presenters", "adapters", "wiring"},
}
OUTSIDE_WORLD = {"subprocess", "urllib", "http", "socket", "os", "webbrowser", "threading", "pathlib", "json", "time"}
OPENS_A_DOOR = {"http", "socket", "socketserver", "asyncio", "xmlrpc", "webbrowser", "multiprocessing"}


def ring_of(module: str) -> str:
    return module.split(".")[1]


def imported_names(path: Path) -> list[tuple[int, str]]:
    found = []
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.append((node.lineno, node.module))
        if isinstance(node, ast.Import):
            found += [(node.lineno, alias.name) for alias in node.names]
    return found


class DependenciesPointInward(unittest.TestCase):
    def test_no_ring_imports_a_ring_outside_it(self):
        breaches = []
        for path in sorted(PACKAGE.rglob("*.py")):
            module = ".".join(path.relative_to(PACKAGE.parent).with_suffix("").parts)
            if module in ("hiru_tsatsi.__main__", "hiru_tsatsi.__init__"):
                continue
            for line, imported in imported_names(path):
                if imported.startswith("hiru_tsatsi.") and ring_of(imported) not in MAY_IMPORT[ring_of(module)]:
                    breaches.append(f"{path.relative_to(PACKAGE.parent)}:{line} imports {imported}")
        self.assertEqual(breaches, [])

    def test_the_core_and_use_cases_never_reach_outside(self):
        for ring in ("work_apps", "use_cases"):
            for path in (PACKAGE / ring).glob("*.py"):
                for line, name in imported_names(path):
                    self.assertNotIn(name.split(".")[0], OUTSIDE_WORLD, f"{path.name}:{line} reaches outside with {name}")

    def test_nothing_listens_for_connections_or_opens_a_browser(self):
        doors = [f"{path.relative_to(PACKAGE.parent)}:{line} imports {name}"
                 for path in sorted(PACKAGE.rglob("*.py"))
                 for line, name in imported_names(path) if name.split(".")[0] in OPENS_A_DOOR]
        self.assertEqual(doors, [])


if __name__ == "__main__":
    unittest.main()
