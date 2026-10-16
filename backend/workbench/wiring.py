import time
from dataclasses import dataclass
from pathlib import Path

from workbench.adapters import this_machine
from workbench.adapters.notify_send import NotifySend
from workbench.adapters.storage import locations
from workbench.adapters.storage.app_list_file import AppListFile
from workbench.adapters.storage.window_name_files import WindowNameFiles
from workbench.use_cases.asking import AskToStart
from workbench.use_cases.editing import EditAppList
from workbench.use_cases.overview import Overview
from workbench.use_cases.ports import Desktop, DesktopSetUp, Notifier, WindowNames
from workbench.use_cases.setting_up import SetUpDesktop
from workbench.use_cases.starting import StartApps


@dataclass(frozen=True)
class App:
    start: StartApps
    ask: AskToStart
    set_up: SetUpDesktop
    edit: EditAppList
    overview: Overview
    notifier: Notifier
    page: Path


def open_app(desktop: Desktop | None = None, app_list: Path | None = None, omastart: Path | None = None,
             notifier: Notifier | None = None, names: WindowNames | None = None, set_up: DesktopSetUp | None = None) -> App:
    store = AppListFile(app_list or locations.app_list_file(), omastart or locations.omastart_file())
    names = names or WindowNameFiles(locations.window_names_folder())
    notifier = notifier or NotifySend()
    desktop = desktop or this_machine.desktop()
    start = StartApps(desktop, store, names, time.monotonic, time.sleep)
    setting_up = SetUpDesktop(set_up or this_machine.set_up(), str(locations.installed_command()))
    return App(start, AskToStart(notifier, start), setting_up, EditAppList(store, desktop), Overview(store, desktop),
               notifier, locations.page_folder())
