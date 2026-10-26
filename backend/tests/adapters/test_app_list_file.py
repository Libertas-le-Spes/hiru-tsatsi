import json
import tempfile
import unittest
from pathlib import Path

from hiru_tsatsi.adapters.storage.app_list_file import AppListFile
from hiru_tsatsi.adapters.storage.app_list_format import from_omastart, from_saved, to_saved
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.workspace import Workspace

OMASTART = {"workspaces": [{"id": 2, "label": "Rider Main",
                            "apps": [{"name": "Rider Main", "cmd": "rider ~/RiderProjects/harbour", "window": None}]}]}
FROM_OMASTART = AppList((Workspace(2, "Rider Main", (App("Rider Main", "rider ~/RiderProjects/harbour"),)),))
FROM_WORKBENCH = AppList((Workspace(1, "Browser", (App("Chat", "chat-app", "chrome-chat"),)),))


class KeepingTheAppList(unittest.TestCase):
    def setUp(self):
        folder = Path(tempfile.mkdtemp())
        self.omastart = folder / "omastart.json"
        self.workbench = folder / "workbench" / "apps.json"
        self.file = AppListFile(folder / "hiru-tsatsi" / "apps.json",
                                [(self.workbench, from_saved), (self.omastart, from_omastart)])

    def test_nothing_saved_anywhere_is_an_empty_list(self):
        self.assertEqual(self.file.load(), AppList())

    def test_the_omastart_list_is_imported_once_and_kept(self):
        self.omastart.write_text(json.dumps(OMASTART))
        self.assertEqual(self.file.load(), FROM_OMASTART)
        self.omastart.write_text(json.dumps({"workspaces": []}))
        self.assertEqual(self.file.load(), FROM_OMASTART)

    def test_the_list_kept_under_the_old_name_comes_before_omastart(self):
        self.omastart.write_text(json.dumps(OMASTART))
        self.workbench.parent.mkdir()
        self.workbench.write_text(json.dumps(to_saved(FROM_WORKBENCH)))
        self.assertEqual(self.file.load(), FROM_WORKBENCH)
        self.assertTrue(self.file.path.exists())

    def test_what_is_saved_comes_back_and_wins_over_earlier_lists(self):
        self.omastart.write_text(json.dumps(OMASTART))
        saved = AppList((Workspace(4, "Comms", (App("Chat", "chat-app", "chat"),)),))
        self.file.save(saved)
        self.assertEqual(self.file.load(), saved)

    def test_an_app_that_opens_in_a_terminal_is_remembered(self):
        saved = AppList((Workspace(2, "Code", (App("Helper", "cd code && helper", "hiru-tsatsi.2-0-helper", True),)),))
        self.file.save(saved)
        self.assertEqual(self.file.load(), saved)

    def test_only_a_real_true_means_a_terminal(self):
        content = {"workspaces": [{"number": 2, "label": "Code", "apps": [
            {"name": "Helper", "command": "helper", "in_terminal": "yes"}]}]}
        self.assertFalse(from_saved(content).placements()[0].app.in_terminal)


if __name__ == "__main__":
    unittest.main()
