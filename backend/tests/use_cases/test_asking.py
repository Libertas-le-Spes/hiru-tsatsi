import unittest

from tests.fakes import FakeClock, FakeDesktop, FakeNames, FakeNotifier, FakeStore, app_list
from workbench.use_cases.asking import AskToStart
from workbench.use_cases.starting import StartApps
from workbench.work_apps.app_list import App

STEAM = App("Steam", "steam")


def ask(clicks: bool):
    desktop = FakeDesktop([])
    clock = FakeClock()
    start = StartApps(desktop, FakeStore(app_list((6, [STEAM]))), FakeNames(), clock, clock.wait)
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
