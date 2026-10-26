import time
from dataclasses import dataclass
from pathlib import Path

from hiru_tsatsi.adapters import this_machine
from hiru_tsatsi.adapters.command_links import SymbolicLinks
from hiru_tsatsi.adapters.notify_send import NotifySend
from hiru_tsatsi.adapters.storage import locations
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile, EarlierList
from hiru_tsatsi.adapters.storage.app_list_format import from_omastart, from_saved
from hiru_tsatsi.adapters.storage.settings_file import SettingsFile
from hiru_tsatsi.adapters.storage.window_name_files import WindowNameFiles
from hiru_tsatsi.presenters.starting_notice import StartingNotice
from hiru_tsatsi.use_cases.asking import AskToStart
from hiru_tsatsi.use_cases.editing import EditAppList
from hiru_tsatsi.use_cases.installing import LinkCommands
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.use_cases.ports import AppListStore, Desktop, DesktopSetUp, Notifier, WindowNames
from hiru_tsatsi.use_cases.setting_up import SetUpDesktop
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.use_cases.window_titles import NamesWhenWanted, WindowTitles
from hiru_tsatsi.work_apps.recognising import Recognising


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


def _store(store: AppListStore | None) -> AppListStore:
    if store is None:
        return AppListFile(locations.app_list_file(), earlier_lists())
    return store


def _titles(titles: WindowTitles | None) -> WindowTitles:
    if titles is None:
        return WindowTitles(SettingsFile(locations.settings_file()), this_machine.window_namer_installed)
    return titles


def _names(titles: WindowTitles, names: WindowNames | None) -> WindowNames:
    if names is None:
        names = WindowNameFiles(locations.window_names_folder())
    return NamesWhenWanted(titles, names)


def _notifier(notifier: Notifier | None) -> Notifier:
    if notifier is None:
        return NotifySend()
    return notifier


def _desktop(desktop: Desktop | None) -> Desktop:
    if desktop is None:
        return this_machine.desktop()
    return desktop


def _set_up(set_up: DesktopSetUp | None) -> DesktopSetUp:
    if set_up is None:
        return this_machine.set_up()
    return set_up


def open_app(desktop: Desktop | None = None, store: AppListStore | None = None, notifier: Notifier | None = None,
             names: WindowNames | None = None, set_up: DesktopSetUp | None = None,
             titles: WindowTitles | None = None) -> Services:
    store = _store(store)
    titles = _titles(titles)
    notifier = _notifier(notifier)
    desktop = _desktop(desktop)
    recognising = Recognising(str(Path.home()))
    start = StartApps(desktop, store, _names(titles, names), time.monotonic, time.sleep, StartingNotice(notifier),
                      recognising)
    setting_up = SetUpDesktop(_set_up(set_up), str(locations.installed_command()))
    return Services(start, AskToStart(notifier, start), setting_up, EditAppList(store, desktop, recognising),
                    Overview(store, desktop, recognising), titles, notifier)


def open_linking(bin_dir: str, launcher: str) -> LinkCommands:
    return LinkCommands(SymbolicLinks(), bin_dir, launcher)
