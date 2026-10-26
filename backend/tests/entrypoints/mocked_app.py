import io
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import create_autospec

from hiru_tsatsi.entrypoints.cli.main import main
from hiru_tsatsi.use_cases.asking import AskToStart
from hiru_tsatsi.use_cases.editing import EditAppList
from hiru_tsatsi.use_cases.overview import Overview
from hiru_tsatsi.use_cases.ports import Notifier
from hiru_tsatsi.use_cases.setting_up import SetUpDesktop
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.use_cases.window_titles import WindowTitles
from hiru_tsatsi.wiring import App


def mocked_app() -> App:
    return App(create_autospec(StartApps, instance=True), create_autospec(AskToStart, instance=True),
               create_autospec(SetUpDesktop, instance=True), create_autospec(EditAppList, instance=True),
               create_autospec(Overview, instance=True), create_autospec(WindowTitles, instance=True),
               create_autospec(Notifier, instance=True))


class Typed:
    def __init__(self, argv: list[str], app: App):
        printed = io.StringIO()
        errors = io.StringIO()
        with redirect_stdout(printed), redirect_stderr(errors):
            self.exit_code = main(argv, app)
        self.printed = printed.getvalue()
        self.errors = errors.getvalue()
