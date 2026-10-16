import json
import tempfile
import unittest
from pathlib import Path

from workbench.adapters.storage.app_list_file import AppListFile
from workbench.work_apps.app_list import App, AppList, Workspace

OMASTART = {"workspaces": [{"id": 2, "label": "Rider Main",
                            "apps": [{"name": "Rider Main", "cmd": "rider ~/RiderProjects/onplia", "window": None}]}]}


class KeepingTheAppList(unittest.TestCase):
    def setUp(self):
        folder = Path(tempfile.mkdtemp())
        self.omastart = folder / "omastart.json"
        self.file = AppListFile(folder / "workbench" / "apps.json", self.omastart)

    def test_nothing_saved_anywhere_is_an_empty_list(self):
        self.assertEqual(self.file.load(), AppList())

    def test_the_omastart_list_is_imported_once_and_kept(self):
        self.omastart.write_text(json.dumps(OMASTART))
        imported = AppList((Workspace(2, "Rider Main", (App("Rider Main", "rider ~/RiderProjects/onplia"),)),))
        self.assertEqual(self.file.load(), imported)
        self.omastart.write_text(json.dumps({"workspaces": []}))
        self.assertEqual(self.file.load(), imported)

    def test_what_is_saved_comes_back_and_wins_over_omastart(self):
        self.omastart.write_text(json.dumps(OMASTART))
        saved = AppList((Workspace(4, "Comms", (App("Chat", "chat-app", "chat"),)),))
        self.file.save(saved)
        self.assertEqual(self.file.load(), saved)


if __name__ == "__main__":
    unittest.main()
