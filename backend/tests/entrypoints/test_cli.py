import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests.fakes import FakeDesktop, FakeNames, FakeNotifier, FakeSetUp, window
from workbench.adapters.storage.app_list_file import AppListFile
from workbench.entrypoints.cli.main import main
from workbench.use_cases.ports import DesktopNotSupported
from workbench.wiring import open_app
from workbench.work_apps.app_list import App, AppList, Workspace


class TheStartCommand(unittest.TestCase):
    def test_reports_what_it_did_on_screen_and_as_a_notification(self):
        folder = Path(tempfile.mkdtemp())
        AppListFile(folder / "apps.json", folder / "none.json").save(
            AppList((Workspace(2, "Rider", (App("Rider Main", "rider onplia", "onplia"),)),)))
        notifier = FakeNotifier()
        desktop = FakeDesktop([window("m", "jetbrains-rider", "onplia – x", 5)])
        app = open_app(desktop, folder / "apps.json", folder / "none.json", notifier, FakeNames(), FakeSetUp())
        printed = io.StringIO()
        with redirect_stdout(printed):
            self.assertEqual(main(["start"], app), 0)
        self.assertEqual(notifier.sent, [("Started 0, 1 already open", "Already open: Rider Main\nMoved to their workspace: Rider Main")])
        self.assertIn("Started 0, 1 already open", printed.getvalue())

    def test_starts_nothing_on_a_desktop_it_cannot_place_windows_on(self):
        def refuse():
            raise DesktopNotSupported("GNOME")
        printed = io.StringIO()
        with redirect_stdout(printed):
            self.assertEqual(main(["start"], opening=refuse), 2)
        self.assertIn("can't place windows on GNOME yet, so it started nothing", printed.getvalue())


if __name__ == "__main__":
    unittest.main()
