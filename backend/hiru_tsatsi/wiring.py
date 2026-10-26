import time

from hiru_tsatsi.adapters import this_machine
from hiru_tsatsi.adapters.command_links import SymbolicLinks
from hiru_tsatsi.adapters.notify_send import NotifySend
from hiru_tsatsi.adapters.storage import locations
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile, EarlierList
from hiru_tsatsi.adapters.storage.app_list_format import from_omastart, from_saved
from hiru_tsatsi.adapters.storage.files import Disk
from hiru_tsatsi.adapters.storage.settings_file import SettingsFile
from hiru_tsatsi.adapters.storage.window_name_files import WindowNameFiles
from hiru_tsatsi.use_cases.asking import AskToStart
from hiru_tsatsi.use_cases.editing import EditAppList
from hiru_tsatsi.use_cases.installing import LinkCommands
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.use_cases.services import Services
from hiru_tsatsi.use_cases.setting_up import SetUpDesktop
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.use_cases.window_titles import NamesWhenWanted, WindowTitles


def earlier_lists() -> list[EarlierList]:
    return [(locations.workbench_list_file(), from_saved), (locations.omastart_file(), from_omastart)]


def open_services() -> Services:
    disk = Disk()
    store = AppListFile(locations.app_list_file(), disk, earlier_lists())
    titles = WindowTitles(SettingsFile(locations.settings_file(), disk), this_machine.window_namer_installed)
    names = NamesWhenWanted(titles, WindowNameFiles(locations.window_names_folder(), disk))
    notifier = NotifySend()
    desktop = this_machine.desktop()
    start = StartApps(desktop, store, names, time.monotonic, time.sleep)
    setting_up = SetUpDesktop(this_machine.set_up(locations.config_home(), disk), str(locations.installed_command()))
    return Services(start, AskToStart(notifier, start), setting_up, EditAppList(store, desktop),
                    Overview(store, desktop), titles, notifier)


def open_linking(bin_dir: str, launcher: str) -> LinkCommands:
    return LinkCommands(SymbolicLinks(), bin_dir, launcher)
