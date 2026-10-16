import time
from dataclasses import dataclass
from pathlib import Path

from workbench.adapters import this_machine
from workbench.adapters.notify_send import NotifySend
from workbench.adapters.storage import locations
from workbench.adapters.storage.app_list_file import AppListFile
from workbench.use_cases.ports import Desktop, Notifier
from workbench.use_cases.starting import StartApps


@dataclass(frozen=True)
class App:
    start: StartApps
    notifier: Notifier


def open_app(desktop: Desktop | None = None, app_list: Path | None = None, omastart: Path | None = None,
             notifier: Notifier | None = None) -> App:
    store = AppListFile(app_list or locations.app_list_file(), omastart or locations.omastart_file())
    start = StartApps(desktop or this_machine.desktop(), store, time.monotonic, time.sleep)
    return App(start, notifier or NotifySend())
