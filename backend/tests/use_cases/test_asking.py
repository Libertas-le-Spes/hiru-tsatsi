import unittest
from unittest.mock import create_autospec

from hiru_tsatsi.use_cases.asking import ACTION, EXPLANATION, QUESTION, AskToStart
from hiru_tsatsi.use_cases.ports import Notifier
from hiru_tsatsi.use_cases.starting import StartApps


def asking(clicks: bool) -> AskToStart:
    notifier = create_autospec(Notifier, instance=True)
    notifier.ask.return_value = clicks
    return AskToStart(notifier, create_autospec(StartApps, instance=True))


class AskingAtLogin(unittest.TestCase):
    def test_asks_once_with_the_question(self):
        ask = asking(clicks=False)
        ask.run()
        ask.notifier.ask.assert_called_once_with(QUESTION, EXPLANATION, ACTION)

    def test_clicking_the_question_starts_the_apps_and_reports_it(self):
        ask = asking(clicks=True)
        self.assertIs(ask.run(), ask.start.run.return_value)
        ask.start.run.assert_called_once_with()

    def test_dismissing_it_starts_nothing(self):
        ask = asking(clicks=False)
        self.assertIsNone(ask.run())
        ask.start.run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
