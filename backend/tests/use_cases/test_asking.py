import unittest

from tests.fakes.app_lists import FakeStore, app_list
from tests.fakes.clock import FakeClock
from tests.fakes.desktop import FakeDesktop
from tests.fakes.notifying import FakeAnnouncer, FakeNotifier
from tests.fakes.recognising import RECOGNISING
from tests.fakes.window_names import FakeNames
from hiru_tsatsi.use_cases.asking import AskToStart
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.work_apps.app import App

STEAM = App("Steam", "steam")


def ask(clicks: bool):
    desktop = FakeDesktop([])
    clock = FakeClock()
    start = StartApps(desktop, FakeStore(app_list((6, [STEAM]))), FakeNames(), clock, clock.wait, FakeAnnouncer(), RECOGNISING)
    return AskToStart(FakeNotifier(clicks), start).run(), desktop


class AskingAtLogin(unittest.TestCase):
    def test_clicking_the_question_starts_the_apps(self):
        outcome, desktop = ask(clicks=True)
        self.assertEqual(desktop.launched, [("steam", 6)])
        self.assertEqual(outcome.started, ["Steam"])

    def test_dismissing_it_starts_nothing(self):
        outcome, desktop = ask(clicks=False)
        self.assertEqual((outcome, desktop.launched), (None, []))


if __name__ == "__main__":
    unittest.main()
