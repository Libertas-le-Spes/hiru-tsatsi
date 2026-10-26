import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from tests.fakes.desktop import FakeDesktop, window
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
from hiru_tsatsi.work_apps.workspace import Workspace


class EditingFromTheCommandLine(unittest.TestCase):
    def setUp(self):
        folder = Path(tempfile.mkdtemp())
        self.file = folder / "apps.json"
        AppListFile(self.file).save(AppList((Workspace(1, "Browser", ()),)))
        self.app = open_app(FakeDesktop([window("c", "chrome-chat.google.com-Default", "Chat", 1)]), self.file,
                            [], FakeNotifier(), FakeNames(), FakeSetUp(), WindowTitles(FakeSettings(), namer_installed))

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

    def test_an_app_and_a_workspace_are_changed_in_place(self):
        main(["add-app", "1", "Chat", "some-browser --chat"], self.app)
        main(["add-app", "1", "Mail", "some-mail"], self.app)
        self.assertEqual(main(["change-app", "1", "0", "Talk", "some-browser --talk"], self.app), 0)
        self.assertEqual(main(["change-workspace", "1", "5", "Comms"], self.app), 0)
        changed = self.saved().workspace(5)
        self.assertEqual((changed.label, [(a.name, a.command) for a in changed.apps]),
                         ("Comms", [("Talk", "some-browser --talk"), ("Mail", "some-mail")]))

    def test_a_refusal_is_said_in_words_and_fails(self):
        errors = io.StringIO()
        with redirect_stderr(errors):
            self.assertEqual(main(["add-workspace", "1", "Again"], self.app), 1)
        self.assertEqual(errors.getvalue(), "Workspace 1 is already in use\n")




if __name__ == "__main__":
    unittest.main()
