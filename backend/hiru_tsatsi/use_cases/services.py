from dataclasses import dataclass

from hiru_tsatsi.use_cases.asking import AskToStart
from hiru_tsatsi.use_cases.editing import EditAppList
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.use_cases.ports import Notifier
from hiru_tsatsi.use_cases.setting_up import SetUpDesktop
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.use_cases.window_titles import WindowTitles


@dataclass(frozen=True)
class Services:
    start: StartApps
    ask: AskToStart
    set_up: SetUpDesktop
    edit: EditAppList
    overview: Overview
    window_titles: WindowTitles
    notifier: Notifier
