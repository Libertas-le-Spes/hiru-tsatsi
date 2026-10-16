import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from tests.fakes import FakeSettings, FakeDesktop, FakeNames, FakeNotifier, FakeSetUp, window
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile
from hiru_tsatsi.entrypoints.web import server
from hiru_tsatsi.use_cases.window_titles import WindowTitles
from hiru_tsatsi.wiring import open_app
from hiru_tsatsi.work_apps.app_list import App, AppList, Workspace


class ThePageServer(unittest.TestCase):
    def setUp(self):
        folder = Path(tempfile.mkdtemp())
        (folder / "page").mkdir()
        (folder / "page" / "index.html").write_text('<meta name="token" content="{{token}}">')
        (folder / "page" / "page.js").write_text("start()")
        self.list_file = folder / "apps.json"
        AppListFile(self.list_file).save(
            AppList((Workspace(1, "Browser", (App("Chat", "chat-app", "chrome-chat"),)),)))
        self.desktop = FakeDesktop([window("c", "chrome-chat-Default", "Chat", 1), window("t", "foot", "~", 4)])
        app = open_app(self.desktop, self.list_file, [], FakeNotifier(), FakeNames(), FakeSetUp(), WindowTitles(FakeSettings(), lambda: True))
        self.page = server.PageServer(app, folder / "page", port=0)
        self.assertTrue(self.page.bind())
        threading.Thread(target=self.page.server.serve_forever, daemon=True).start()
        self.addCleanup(self.page.server.server_close)
        self.addCleanup(self.page.server.shutdown)

    def call(self, path, body=None, token=True, host=None):
        request = urllib.request.Request(f"http://127.0.0.1:{self.page.port}{path}",
                                         data=json.dumps(body).encode() if body is not None else None)
        request.add_header("Host", host or f"127.0.0.1:{self.page.port}")
        if token:
            request.add_header("X-Hiru-Tsatsi-Token", self.page.token)
        try:
            with urllib.request.urlopen(request) as answer:
                return answer.status, answer.read().decode()
        except urllib.error.HTTPError as refused:
            return refused.code, refused.read().decode()

    def test_the_page_carries_its_token_and_its_files_are_served(self):
        self.assertEqual(self.call("/", token=False), (200, f'<meta name="token" content="{self.page.token}">'))
        self.assertEqual(self.call("/page.js", token=False), (200, "start()"))

    def test_the_list_needs_the_token(self):
        self.assertEqual(self.call("/api/list", token=False)[0], 403)
        status, body = self.call("/api/list")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["workspaces"][0]["apps"][0]["status"], "✓ Chat, open on workspace 1")

    def test_another_host_name_is_refused_even_with_the_token(self):
        self.assertEqual(self.call("/", host="evil.example").__getitem__(0), 403)
        self.assertEqual(self.call("/api/list", host=f"evil.example:{self.page.port}")[0], 403)

    def test_a_change_is_saved_and_answered_with_the_new_list(self):
        status, body = self.call("/api/workspace/add", {"number": 4, "label": "Comms"})
        self.assertEqual(status, 200)
        self.assertEqual([s["number"] for s in json.loads(body)["workspaces"]], [1, 4])
        self.assertEqual([s["number"] for s in json.loads(self.list_file.read_text())["workspaces"]], [1, 4])

    def test_a_refusal_comes_back_in_words(self):
        status, body = self.call("/api/workspace/add", {"number": 1, "label": "Again"})
        self.assertEqual((status, json.loads(body)), (409, {"error": "Workspace 1 is already in use"}))

    def test_a_malformed_change_is_refused_without_harm(self):
        self.assertEqual(self.call("/api/workspace/add", {"label": "No number"})[0], 400)

    def test_windows_to_choose_from_and_starting_from_the_page(self):
        status, body = self.call("/api/windows?workspace=1&index=0")
        self.assertEqual([w["address"] for w in json.loads(body)["windows"]], ["c", "t"])
        status, body = self.call("/api/start", {})
        self.assertEqual((status, json.loads(body)["summary"]), (200, "Started 0, 1 already open"))

    def test_window_titles_are_shown_and_switched_from_the_page(self):
        self.assertTrue(json.loads(self.call("/api/list")[1])["windowTitles"])
        status, body = self.call("/api/window-titles", {"on": False})
        self.assertEqual((status, json.loads(body)["windowTitles"]), (200, False))
        self.assertEqual(self.call("/api/window-titles", {"on": "no"})[0], 400)

    def test_a_second_edit_opens_the_page_already_running(self):
        opened = []
        self.assertEqual(server.serve(self.page.app, self.page.pages, opened.append, port=self.page.port), "already open")
        self.assertEqual(opened, [server.page_url(self.page.port)])



class StoppingAfterThePageCloses(unittest.TestCase):
    def test_stops_once_the_page_has_been_quiet_long_enough(self):
        now = [0.0]
        page = server.PageServer(None, Path("."), port=0, clock=lambda: now[0])
        page.server = type("Quiet", (), {"serve_forever": lambda self: None, "shutdown": lambda self: None,
                                         "server_close": lambda self: None})()
        running = threading.Thread(target=page.serve_until_closed, kwargs={"closed_after": 120, "check_every": 0.01})
        running.start()
        now[0] = 60.0
        page.seen()
        now[0] = 150.0
        running.join(0.3)
        self.assertTrue(running.is_alive(), "stopped although the page checked in 90 seconds ago")
        now[0] = 181.0
        running.join(1)
        self.assertFalse(running.is_alive())


if __name__ == "__main__":
    unittest.main()
