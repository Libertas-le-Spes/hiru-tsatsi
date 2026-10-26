import time
from pathlib import Path

from hiru_tsatsi.adapters import this_machine
from hiru_tsatsi.adapters.command_links import SymbolicLinks
from hiru_tsatsi.adapters.front_process import FrontProcess
from hiru_tsatsi.adapters.notify_send import NotifySend
from hiru_tsatsi.adapters.proc_files import ProcFiles
from hiru_tsatsi.adapters.seeing_inside import SeeingInside
from hiru_tsatsi.adapters.storage import locations
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile, EarlierList
from hiru_tsatsi.adapters.storage.app_list_format import from_omastart, from_saved
from hiru_tsatsi.adapters.storage.files import Disk
from hiru_tsatsi.adapters.storage.settings_file import SettingsFile
from hiru_tsatsi.adapters.storage.window_name_files import WindowNameFiles
from hiru_tsatsi.adapters.tagged_launch import TaggedLaunches
from hiru_tsatsi.adapters.terminal import XdgTerminal
from hiru_tsatsi.presenters.starting_notice import StartingNotice
from hiru_tsatsi.use_cases.asking import AskToStart
from hiru_tsatsi.use_cases.editing import EditAppList
from hiru_tsatsi.use_cases.installing import LinkCommands
from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.use_cases.services import Services
from hiru_tsatsi.use_cases.setting_up import SetUpDesktop
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.use_cases.window_titles import NamesWhenWanted, WindowTitles
from hiru_tsatsi.work_apps.recognising import Recognising


def earlier_lists() -> list[EarlierList]:
    return [(locations.workbench_list_file(), from_saved), (locations.omastart_file(), from_omastart)]


def open_services() -> Services:
    disk = Disk()
    processes = ProcFiles()
    store = AppListFile(locations.app_list_file(), disk, earlier_lists())
    titles = WindowTitles(SettingsFile(locations.settings_file(), disk), this_machine.window_namer_installed)
    names = NamesWhenWanted(titles, WindowNameFiles(locations.window_names_folder(), disk))
    notifier = NotifySend()
    desktop = SeeingInside(this_machine.desktop(), FrontProcess(processes).of_window)
    recognising = Recognising(str(Path.home()))
    launcher = Launcher(desktop, TaggedLaunches(processes), XdgTerminal())
    start = StartApps(desktop, launcher, store, names, time.monotonic, time.sleep, StartingNotice(notifier),
                      recognising)
    setting_up = SetUpDesktop(this_machine.set_up(locations.config_home(), disk), str(locations.installed_command()))
    return Services(start, AskToStart(notifier, start), setting_up, EditAppList(store, desktop, recognising),
                    Overview(store, desktop, recognising), titles, notifier)


def open_linking(bin_dir: str, launcher_path: str) -> LinkCommands:
    return LinkCommands(SymbolicLinks(), bin_dir, launcher_path)
