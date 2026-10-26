import time
from dataclasses import dataclass

from hiru_tsatsi.adapters import this_machine
from hiru_tsatsi.adapters.command_links import SymbolicLinks
from hiru_tsatsi.adapters.notify_send import NotifySend
from hiru_tsatsi.adapters.storage import locations
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile, EarlierList
from hiru_tsatsi.adapters.storage.app_list_format import from_omastart, from_saved
from hiru_tsatsi.adapters.storage.settings_file import SettingsFile
from hiru_tsatsi.adapters.storage.window_name_files import WindowNameFiles
from hiru_tsatsi.use_cases.asking import AskToStart
from hiru_tsatsi.use_cases.editing import EditAppList
from hiru_tsatsi.use_cases.installing import LinkCommands
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.use_cases.ports import Notifier
from hiru_tsatsi.use_cases.setting_up import SetUpDesktop
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.use_cases.window_titles import NamesWhenWanted, WindowTitles


@dataclass(frozen=True)
class Services:
    start: StartApps
    ask: AskToStart
    set_up: SetUpDesktop
    edit: EditAppList
    overview: Overview
    window_titles: WindowTitles
    notifier: Notifier


def earlier_lists() -> list[EarlierList]:
    return [(locations.workbench_list_file(), from_saved), (locations.omastart_file(), from_omastart)]


def open_services() -> Services:
    store = AppListFile(locations.app_list_file(), earlier_lists())
    titles = WindowTitles(SettingsFile(locations.settings_file()), this_machine.window_namer_installed)
    names = NamesWhenWanted(titles, WindowNameFiles(locations.window_names_folder()))
    notifier = NotifySend()
    desktop = this_machine.desktop()
    start = StartApps(desktop, store, names, time.monotonic, time.sleep)
    setting_up = SetUpDesktop(this_machine.set_up(), str(locations.installed_command()))
    return Services(start, AskToStart(notifier, start), setting_up, EditAppList(store, desktop),
                    Overview(store, desktop), titles, notifier)


def open_linking(bin_dir: str, launcher: str) -> LinkCommands:
    return LinkCommands(SymbolicLinks(), bin_dir, launcher)
