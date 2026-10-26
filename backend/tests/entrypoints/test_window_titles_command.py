import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests.fakes.desktop import FakeDesktop
from tests.fakes.notifying import FakeNotifier
from tests.fakes.set_up import FakeSetUp
from tests.fakes.settings import FakeSettings
from tests.fakes.window_names import FakeNames
from tests.fakes.window_names import namer_installed
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile
from hiru_tsatsi.entrypoints.cli.main import main
from hiru_tsatsi.use_cases.window_titles import WindowTitles
from hiru_tsatsi.wiring import open_app
from hiru_tsatsi.work_apps.app_list import AppList


class TheWindowTitlesCommand(unittest.TestCase):
    def test_says_why_and_turns_off(self):
        folder = Path(tempfile.mkdtemp())
        AppListFile(folder / "apps.json").save(AppList())
        app = open_app(FakeDesktop([]), folder / "apps.json", [], FakeNotifier(), FakeNames(), FakeSetUp(),
                       WindowTitles(FakeSettings(), namer_installed))
        said = io.StringIO()
        with redirect_stdout(said):
            main(["window-titles"], app)
            main(["window-titles", "off"], app)
        self.assertEqual(said.getvalue().splitlines(), [
            "Window titles are on, because window-names is installed. Turn them on or off with `hiru-tsatsi window-titles on` or `off`.",
            "Window titles are off, as you chose. Turn them on or off with `hiru-tsatsi window-titles on` or `off`."])


if __name__ == "__main__":
    unittest.main()




if __name__ == "__main__":
    unittest.main()
