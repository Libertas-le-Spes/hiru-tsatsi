import io
import unittest
from contextlib import redirect_stdout

from tests.entrypoints.mocked_app import Typed, mocked_app
from hiru_tsatsi.entrypoints.cli.main import main
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.ports import DesktopNotSupported

OUTCOME = Outcome(already_open=["Rider Main"], moved=["Rider Main"])
SUMMARY = "Started 0, 1 already open"
DETAILS = "Already open: Rider Main\nMoved to their workspace: Rider Main"


class TheStartCommand(unittest.TestCase):
    def test_starts_once_and_reports_on_screen_and_as_a_notification(self):
        app = mocked_app()
        app.start.run.return_value = OUTCOME
        typed = Typed(["start"], app)
        app.start.run.assert_called_once_with()
        app.notifier.notify.assert_called_once_with(SUMMARY, DETAILS)
        self.assertEqual((typed.exit_code, typed.printed), (0, f"{SUMMARY}\n{DETAILS}\n"))

    def test_starts_nothing_on_a_desktop_it_cannot_place_windows_on(self):
        def refuse():
            raise DesktopNotSupported("GNOME")
        printed = io.StringIO()
        with redirect_stdout(printed):
            self.assertEqual(main(["start"], opening=refuse), 2)
        self.assertIn("can't place windows on GNOME yet, so it started nothing", printed.getvalue())


class TheAskCommand(unittest.TestCase):
    def test_a_dismissed_question_reports_nothing(self):
        app = mocked_app()
        app.ask.run.return_value = None
        typed = Typed(["ask"], app)
        app.notifier.notify.assert_not_called()
        self.assertEqual((typed.exit_code, typed.printed), (0, ""))

    def test_a_clicked_question_reports_what_started(self):
        app = mocked_app()
        app.ask.run.return_value = OUTCOME
        Typed(["ask"], app)
        app.notifier.notify.assert_called_once_with(SUMMARY, DETAILS)


if __name__ == "__main__":
    unittest.main()
