import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests.fakes.desktop import FakeDesktop, window
from tests.fakes.notifying import FakeNotifier
from tests.fakes.set_up import FakeSetUp
from tests.fakes.window_names import FakeNames
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile
from hiru_tsatsi.entrypoints.cli.main import main
from hiru_tsatsi.wiring import open_app
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.workspace import Workspace


class WhatTheBarPanelAsks(unittest.TestCase):
    def setUp(self):
        folder = Path(tempfile.mkdtemp())
        self.file = folder / "apps.json"
        AppListFile(self.file).save(AppList((Workspace(1, "Browser", (App("Boards", "some-browser --boards"),)),)))
        desktop = FakeDesktop([window("0xg", "chrome-gitlab.com-Default", "Issue Boards", 4), window("0xt", "foot", "~", 4)])
        self.app = open_app(desktop, self.file, [], FakeNotifier(), FakeNames(), FakeSetUp())

    def said(self, argv):
        out = io.StringIO()
        with redirect_stdout(out):
            main(argv, self.app)
        return out.getvalue()

    def test_overview_and_choosing_a_window_and_forgetting_it(self):
        self.assertEqual(json.loads(self.said(["overview"]))["workspaces"][0]["apps"][0]["status"],
                         "Will be recognised the first time Hiru Tsatsi starts it")
        self.assertEqual([w["address"] for w in json.loads(self.said(["windows-for", "1", "0"]))], ["0xg", "0xt"])
        self.said(["choose-window", "1", "0", "0xg"])
        self.assertEqual(json.loads(self.said(["overview"]))["workspaces"][0]["apps"][0]["status"],
                         "✓ Issue Boards, open on workspace 4 (moved to 1 when you start)")
        self.said(["forget-window", "1", "0"])
        self.assertFalse(json.loads(self.said(["overview"]))["workspaces"][0]["apps"][0]["knowsWindow"])


if __name__ == "__main__":
    unittest.main()
