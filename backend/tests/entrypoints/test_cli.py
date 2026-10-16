import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tests.fakes import FakeSettings, FakeDesktop, FakeNames, FakeNotifier, FakeSetUp, window
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile
from hiru_tsatsi.entrypoints.cli.main import main
from hiru_tsatsi.use_cases.ports import DesktopNotSupported
from hiru_tsatsi.use_cases.window_titles import WindowTitles
from hiru_tsatsi.wiring import open_app
from hiru_tsatsi.work_apps.app_list import App, AppList, Workspace


class TheStartCommand(unittest.TestCase):
    def test_reports_what_it_did_on_screen_and_as_a_notification(self):
        folder = Path(tempfile.mkdtemp())
        AppListFile(folder / "apps.json").save(
            AppList((Workspace(2, "Rider", (App("Rider Main", "rider harbour", "harbour"),)),)))
        notifier = FakeNotifier()
        desktop = FakeDesktop([window("m", "jetbrains-rider", "harbour – x", 5)])
        app = open_app(desktop, folder / "apps.json", [], notifier, FakeNames(), FakeSetUp(), WindowTitles(FakeSettings(), lambda: True))
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


class TheWindowTitlesCommand(unittest.TestCase):
    def test_says_why_and_turns_off(self):
        folder = Path(tempfile.mkdtemp())
        AppListFile(folder / "apps.json").save(AppList())
        app = open_app(FakeDesktop([]), folder / "apps.json", [], FakeNotifier(), FakeNames(), FakeSetUp(),
                       WindowTitles(FakeSettings(), lambda: True))
        said = io.StringIO()
        with redirect_stdout(said):
            main(["window-titles"], app)
            main(["window-titles", "off"], app)
        self.assertEqual(said.getvalue().splitlines(), [
            "Window titles are on, because window-names is installed. Turn them on or off with `hiru-tsatsi window-titles on` or `off`.",
            "Window titles are off, as you chose. Turn them on or off with `hiru-tsatsi window-titles on` or `off`."])


if __name__ == "__main__":
    unittest.main()


class EditingFromTheCommandLine(unittest.TestCase):
    def setUp(self):
        folder = Path(tempfile.mkdtemp())
        self.file = folder / "apps.json"
        AppListFile(self.file).save(AppList((Workspace(1, "Browser", ()),)))
        self.app = open_app(FakeDesktop([window("c", "chrome-chat.google.com-Default", "Chat", 1)]), self.file,
                            [], FakeNotifier(), FakeNames(), FakeSetUp(), WindowTitles(FakeSettings(), lambda: True))

    def saved(self):
        return AppListFile(self.file).load()

    def test_workspaces_and_apps_are_added_and_removed(self):
        self.assertEqual(main(["add-workspace", "4", "Comms"], self.app), 0)
        self.assertEqual(main(["add-app", "1", "Chat", "omarchy-launch-webapp https://chat.google.com/"], self.app), 0)
        self.assertEqual([s.number for s in self.saved().workspaces], [1, 4])
        self.assertEqual(self.saved().workspace(1).apps[0].learned_window, "chrome-chat.google.com-Default")
        self.assertEqual(main(["remove-app", "1", "0"], self.app), 0)
        self.assertEqual(main(["remove-workspace", "4"], self.app), 0)
        self.assertEqual(self.saved(), AppList((Workspace(1, "Browser", ()),)))

    def test_a_refusal_is_said_in_words_and_fails(self):
        errors = io.StringIO()
        with redirect_stderr(errors):
            self.assertEqual(main(["add-workspace", "1", "Again"], self.app), 1)
        self.assertEqual(errors.getvalue(), "Workspace 1 is already in use\n")
