import unittest

from tests.examples.clock import TickingClock
from tests.examples.home import RECOGNISING
from tests.examples.windows import window
from tests.use_cases.mocked_list import desktop_showing
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals, Trial
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.windows import Window

HELPER = Placement(2, 0, App("Helper", "cd code && helper"))
TERMINAL = window("t", "hiru-tsatsi.helper-1a2b3c4d", "foot", 2)


def with_inside(program: str, folder: str) -> Window:
    return window("t", "hiru-tsatsi.helper-1a2b3c4d", "foot", 2, program, folder)


class ConfirmingATrialTerminal(unittest.TestCase):
    def setUp(self):
        self.clock = TickingClock()

    def confirmed_while_showing(self, windows: list[Window]) -> list[Placement]:
        confirming = ConfirmingTerminals(desktop_showing(windows), self.clock, RECOGNISING, 60.0)
        return confirming.confirmed_among([Trial(HELPER, TERMINAL)])

    def test_confirms_at_once_when_the_apps_program_runs_in_it(self):
        self.assertEqual(self.confirmed_while_showing([with_inside("helper", "/home/sam/code")]), [HELPER])
        self.assertEqual(self.clock.seconds, 0.0)

    def test_keeps_looking_until_the_program_starts(self):
        desktop = desktop_showing([])
        desktop.windows.side_effect = [[with_inside("sh", "/home/sam")], [with_inside("helper", "/home/sam/code")]]
        confirming = ConfirmingTerminals(desktop, self.clock, RECOGNISING, 60.0)
        self.assertEqual(confirming.confirmed_among([Trial(HELPER, TERMINAL)]), [HELPER])

    def test_gives_up_after_its_time_when_only_a_shell_runs_in_it(self):
        self.assertEqual(self.confirmed_while_showing([with_inside("sh", "/home/sam")]), [])
        self.assertGreaterEqual(self.clock.seconds, 60.0)

    def test_the_same_program_in_another_window_does_not_count(self):
        elsewhere = window("x", "foot", "", 2, "helper", "/home/sam/code")
        self.assertEqual(self.confirmed_while_showing([elsewhere]), [])


if __name__ == "__main__":
    unittest.main()
