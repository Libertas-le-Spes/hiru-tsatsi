import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import Mock, call

from tests.entrypoints.mocked_services import Typed, mocked_services
from hiru_tsatsi.entrypoints.cli.main import main
from hiru_tsatsi.use_cases.failures import AlreadyStarting, DesktopNotSupported
from hiru_tsatsi.use_cases.offering_terminals import TerminalOffer
from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement

OUTCOME = Outcome(already_open=["Rider Main"], moved=["Rider Main"])
HELPER = Placement(2, 0, App("Helper", "cd code && helper"))
SUMMARY = "Started 0, 1 already open"
DETAILS = "Already open: Rider Main\nMoved to their workspace: Rider Main"


class TheStartCommand(unittest.TestCase):
    def test_starts_once_and_reports_on_screen_and_as_a_notification(self):
        services = mocked_services()
        services.start.run.return_value = OUTCOME
        typed = Typed(["start"], services)
        services.start.run.assert_called_once_with()
        services.notifier.notify.assert_called_once_with(SUMMARY, DETAILS)
        self.assertEqual((typed.exit_code, typed.printed), (0, f"{SUMMARY}\n{DETAILS}\n"))

    def test_reports_the_start_before_offering_a_terminal_for_what_stopped(self):
        services = mocked_services()
        services.start.run.return_value = Outcome(started=["Helper"], stopped_without_window=[HELPER])
        in_order = Mock()
        in_order.attach_mock(services.notifier.notify, "notify")
        in_order.attach_mock(services.offer.run, "offer")
        Typed(["start"], services)
        self.assertEqual(in_order.mock_calls[1], call.offer([HELPER]))
        self.assertEqual(in_order.mock_calls[0].args[0], "Started 1, 0 already open")

    def test_reports_what_the_terminal_offer_settled(self):
        services = mocked_services()
        services.start.run.return_value = OUTCOME
        services.offer.run.return_value = TerminalOffer(now_opens_in_terminal=["Helper"])
        Typed(["start"], services)
        services.notifier.notify.assert_called_with("Work apps in a terminal", "Now opens in a terminal: Helper")

    def test_a_refused_start_says_so_on_screen_too(self):
        services = mocked_services()
        services.start.run.side_effect = AlreadyStarting()
        typed = Typed(["start"], services)
        services.notifier.notify.assert_called_once_with("Work apps not started", AlreadyStarting().explained())
        self.assertEqual(typed.exit_code, 1)

    def test_starts_nothing_on_a_desktop_it_cannot_place_windows_on(self):
        def refuse():
            raise DesktopNotSupported("GNOME")
        errors = io.StringIO()
        with redirect_stderr(errors):
            self.assertEqual(main(["start"], refuse), 2)
        self.assertIn("can't place windows on GNOME yet, so it did nothing", errors.getvalue())


class TheAskCommand(unittest.TestCase):
    def test_a_dismissed_question_reports_nothing(self):
        services = mocked_services()
        services.ask.run.return_value = None
        typed = Typed(["ask"], services)
        services.notifier.notify.assert_not_called()
        self.assertEqual((typed.exit_code, typed.printed), (0, ""))

    def test_a_clicked_question_reports_what_started(self):
        services = mocked_services()
        services.ask.run.return_value = OUTCOME
        Typed(["ask"], services)
        services.notifier.notify.assert_called_once_with(SUMMARY, DETAILS)


if __name__ == "__main__":
    unittest.main()
