import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests.fakes.desktop import FakeDesktop, window
from tests.fakes.notifying import FakeNotifier
from tests.fakes.set_up import FakeSetUp
from tests.fakes.settings import FakeSettings
from tests.fakes.window_names import FakeNames
from tests.fakes.window_names import namer_installed
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile
from hiru_tsatsi.entrypoints.cli.main import main
from hiru_tsatsi.use_cases.ports import DesktopNotSupported
from hiru_tsatsi.use_cases.window_titles import WindowTitles
from hiru_tsatsi.wiring import open_app
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.workspace import Workspace


class TheStartCommand(unittest.TestCase):
    def test_reports_what_it_did_on_screen_and_as_a_notification(self):
        folder = Path(tempfile.mkdtemp())
        AppListFile(folder / "apps.json").save(
            AppList((Workspace(2, "Rider", (App("Rider Main", "rider harbour", "harbour"),)),)))
        notifier = FakeNotifier()
        desktop = FakeDesktop([window("m", "jetbrains-rider", "harbour – x", 5)])
        app = open_app(desktop, folder / "apps.json", [], notifier, FakeNames(), FakeSetUp(), WindowTitles(FakeSettings(), namer_installed))
        printed = io.StringIO()
        with redirect_stdout(printed):
            self.assertEqual(main(["start"], app), 0)
        self.assertEqual(notifier.sent, [("Started 0, 1 already open", "Already open: Rider Main\nMoved to their workspace: Rider Main")])
        self.assertIn("Started 0, 1 already open", printed.getvalue())

    def test_says_which_apps_are_starting_as_soon_as_it_begins(self):
        folder = Path(tempfile.mkdtemp())
        AppListFile(folder / "apps.json").save(AppList((Workspace(3, "Games", (App("Steam", "steam"),)),)))
        notifier = FakeNotifier()
        desktop = FakeDesktop([], {"steam": [window("s", "steam", "Steam", 3)]})
        app = open_app(desktop, folder / "apps.json", [], notifier, FakeNames(), FakeSetUp(), WindowTitles(FakeSettings(), namer_installed))
        with redirect_stdout(io.StringIO()):
            main(["start"], app)
        self.assertEqual(notifier.sent[0], ("Starting 1 work app", "Steam"))

    def test_starts_nothing_on_a_desktop_it_cannot_place_windows_on(self):
        def refuse():
            raise DesktopNotSupported("GNOME")
        printed = io.StringIO()
        with redirect_stdout(printed):
            self.assertEqual(main(["start"], opening=refuse), 2)
        self.assertIn("can't place windows on GNOME yet, so it started nothing", printed.getvalue())




if __name__ == "__main__":
    unittest.main()
