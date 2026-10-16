import time
from dataclasses import dataclass
from pathlib import Path

from hiru_tsatsi.adapters import this_machine
from hiru_tsatsi.adapters.notify_send import NotifySend
from hiru_tsatsi.adapters.storage import locations
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile, EarlierList, from_omastart, from_saved
from hiru_tsatsi.adapters.storage.settings_file import SettingsFile
from hiru_tsatsi.adapters.storage.window_name_files import WindowNameFiles
from hiru_tsatsi.use_cases.asking import AskToStart
from hiru_tsatsi.use_cases.editing import EditAppList
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.use_cases.ports import Desktop, DesktopSetUp, Notifier, WindowNames
from hiru_tsatsi.use_cases.setting_up import SetUpDesktop
from hiru_tsatsi.use_cases.window_titles import NamesWhenWanted, WindowTitles
from hiru_tsatsi.use_cases.starting import StartApps


@dataclass(frozen=True)
class App:
    start: StartApps
    ask: AskToStart
    set_up: SetUpDesktop
    edit: EditAppList
    overview: Overview
    window_titles: WindowTitles
    notifier: Notifier
    page: Path


def earlier_lists() -> list[EarlierList]:
    return [(locations.workbench_list_file(), from_saved), (locations.omastart_file(), from_omastart)]


def open_app(desktop: Desktop | None = None, app_list: Path | None = None, earlier: list[EarlierList] | None = None,
             notifier: Notifier | None = None, names: WindowNames | None = None, set_up: DesktopSetUp | None = None,
             titles: WindowTitles | None = None) -> App:
    store = AppListFile(app_list or locations.app_list_file(), earlier_lists() if earlier is None else earlier)
    titles = titles or WindowTitles(SettingsFile(locations.settings_file()), this_machine.window_namer_installed)
    names = NamesWhenWanted(titles, names or WindowNameFiles(locations.window_names_folder()))
    notifier = notifier or NotifySend()
    desktop = desktop or this_machine.desktop()
    start = StartApps(desktop, store, names, time.monotonic, time.sleep)
    setting_up = SetUpDesktop(set_up or this_machine.set_up(), str(locations.installed_command()))
    return App(start, AskToStart(notifier, start), setting_up, EditAppList(store, desktop), Overview(store, desktop),
               titles, notifier, locations.page_folder())
