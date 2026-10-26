import hashlib
import re

from hiru_tsatsi.work_apps.app import App

NOT_IN_A_WINDOW_NAME = re.compile(r"[^a-z0-9]+")
FINGERPRINT_LENGTH = 8


def _name_part(name: str) -> str:
    part = NOT_IN_A_WINDOW_NAME.sub("-", name.lower()).strip("-")
    if part == "":
        return "app"
    return part


def _fingerprint(command: str) -> str:
    return hashlib.sha256(command.encode()).hexdigest()[:FINGERPRINT_LENGTH]


def terminal_window_name(app: App) -> str:
    return f"hiru-tsatsi.{_name_part(app.name)}-{_fingerprint(app.command)}"


def in_a_terminal(app: App) -> App:
    return app.opening_in_terminal(terminal_window_name(app))
