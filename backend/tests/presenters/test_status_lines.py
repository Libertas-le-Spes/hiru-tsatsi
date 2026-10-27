import unittest

from tests.examples.windows import window
from hiru_tsatsi.presenters.status_lines import status_line
from hiru_tsatsi.use_cases.overview import AppView
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement

KNOWN = Placement(2, 0, App("Rider Main", "rider ~/code/harbour", "harbour"))
UNKNOWN = Placement(2, 1, App("Steam", "steam"))


class SayingWhereAnAppsWindowIs(unittest.TestCase):
    def test_open_on_its_own_workspace(self):
        view = AppView(KNOWN, window("m", "jetbrains-rider", "harbour – x", 2))
        self.assertEqual(status_line(view), "✓ harbour – x, open on workspace 2")

    def test_open_elsewhere_says_where_it_will_be_moved(self):
        view = AppView(KNOWN, window("m", "jetbrains-rider", "harbour – x", 4))
        self.assertEqual(status_line(view), "✓ harbour – x, open on workspace 4 (moved to 2 when you start)")

    def test_closed_and_opening_in_a_terminal(self):
        self.assertEqual(status_line(AppView(KNOWN, None, opens_in_terminal=True)),
                         "Opens in a terminal, recognised when it opens")

    def test_closed_but_known(self):
        self.assertEqual(status_line(AppView(KNOWN, None)), "Recognised when it opens")

    def test_never_seen(self):
        self.assertEqual(status_line(AppView(UNKNOWN, None)), "Will be recognised the first time Hiru Tsatsi starts it")


if __name__ == "__main__":
    unittest.main()
