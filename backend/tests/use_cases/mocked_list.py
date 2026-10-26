from unittest.mock import Mock, create_autospec

from hiru_tsatsi.use_cases.ports import AppListStore, Desktop
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.windows import Window


def store_holding(apps: AppList) -> Mock:
    store = create_autospec(AppListStore, instance=True)
    store.load.return_value = apps
    return store


def desktop_showing(windows: list[Window]) -> Mock:
    desktop = create_autospec(Desktop, instance=True)
    desktop.windows.return_value = windows
    return desktop


def saved_once(store: Mock) -> AppList:
    store.save.assert_called_once()
    return store.save.call_args.args[0]
