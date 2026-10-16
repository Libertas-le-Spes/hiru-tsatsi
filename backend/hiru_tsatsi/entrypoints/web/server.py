import json
import re
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qsl, urlparse

from hiru_tsatsi.entrypoints.web import requests
from hiru_tsatsi.presenters.page_state import page_state
from hiru_tsatsi.work_apps.app_list import Refused

PORT = 47640
CLOSED_PAGE_SECONDS = 120
PAGE_FILE = re.compile(r"^/[a-z_]+\.(js|css)$")
CONTENT_TYPES = {"js": "text/javascript", "css": "text/css"}


def page_url(port: int) -> str:
    return f"http://127.0.0.1:{port}/"


class PageServer:
    def __init__(self, app, pages: Path, port: int = PORT, clock: Callable[[], float] = time.monotonic):
        self.app = app
        self.pages = pages
        self.port = port
        self.clock = clock
        self.token = secrets.token_urlsafe(32)
        self.last_seen = clock()
        self.lock = threading.Lock()
        self.server: ThreadingHTTPServer | None = None

    def bind(self) -> bool:
        try:
            self.server = ThreadingHTTPServer(("127.0.0.1", self.port), _handler(self))
        except OSError:
            return False
        self.port = self.server.server_address[1]
        return True

    def serve_until_closed(self, closed_after: float = CLOSED_PAGE_SECONDS, check_every: float = 5.0) -> None:
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        while self.clock() - self.last_seen < closed_after:
            time.sleep(check_every)
        self.server.shutdown()
        self.server.server_close()

    def seen(self) -> None:
        self.last_seen = self.clock()


def serve(app, pages: Path, open_page: Callable[[str], object], port: int = PORT) -> str:
    server = PageServer(app, pages, port)
    if not server.bind():
        open_page(page_url(port))
        return "already open"
    open_page(page_url(server.port))
    server.serve_until_closed()
    return "closed"


def _page_file(pages: Path, path: str, token: str) -> tuple[str, bytes] | None:
    if path == "/":
        page = (pages / "index.html").read_text(encoding="utf-8").replace("{{token}}", token)
        return "text/html; charset=utf-8", page.encode("utf-8")
    if not PAGE_FILE.match(path) or not (pages / path.lstrip("/")).is_file():
        return None
    return f"{CONTENT_TYPES[path.rsplit('.', 1)[1]]}; charset=utf-8", (pages / path.lstrip("/")).read_bytes()


def _handler(page: PageServer) -> type[BaseHTTPRequestHandler]:
    reads, changes, actions = requests.reads(page.app), requests.changes(page.app), requests.actions(page.app)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return None

        def _local(self) -> bool:
            return self.headers.get("Host") in {f"127.0.0.1:{page.port}", f"localhost:{page.port}"}

        def _trusted(self) -> bool:
            return self._local() and secrets.compare_digest(self.headers.get("X-Hiru-Tsatsi-Token", ""), page.token)

        def do_GET(self):
            if not self._local():
                return self._send(403, "text/plain", b"forbidden")
            page.seen()
            address = urlparse(self.path)
            page_file = _page_file(page.pages, address.path, page.token)
            if page_file:
                return self._send(200, *page_file)
            if not self._trusted():
                return self._json(403, {"error": "forbidden"})
            if address.path not in reads:
                return self._json(404, {"error": "not found"})
            return self._answer(lambda: reads[address.path](dict(parse_qsl(address.query))))

        def do_POST(self):
            if not self._trusted():
                return self._json(403, {"error": "forbidden"})
            page.seen()
            body = self._body()
            if self.path in actions:
                return self._answer(lambda: actions[self.path](body))
            if self.path in changes:
                return self._answer(lambda: self._changed(changes[self.path], body))
            return self._json(404, {"error": "not found"})

        def _changed(self, change, body: dict) -> dict:
            change(body)
            return page_state(page.app.overview.run(), page.app.window_titles.wanted())

        def _answer(self, work) -> None:
            try:
                with page.lock:
                    result = work()
            except Refused as refused:
                return self._json(409, {"error": str(refused)})
            except (KeyError, ValueError):
                return self._json(400, {"error": "The page sent something Hiru Tsatsi did not understand"})
            return self._json(200, result)

        def _body(self) -> dict:
            length = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                return {}
            return body if isinstance(body, dict) else {}

        def _json(self, status: int, content: dict) -> None:
            self._send(status, "application/json", json.dumps(content).encode("utf-8"))

        def _send(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    return Handler
