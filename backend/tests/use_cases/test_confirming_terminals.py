import unittest

from tests.examples.home import RECOGNISING
from tests.examples.windows import window
from hiru_tsatsi.use_cases.confirming_terminals import ConfirmingTerminals
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement

HELPER = Placement(2, 0, App("Helper", "cd code && helper"))
TERMINAL = window("t", "hiru-tsatsi.helper-1a2b3c4d", "foot", 2)


def with_inside(program: str, folder: str):
    return window("t", "hiru-tsatsi.helper-1a2b3c4d", "foot", 2, program, folder)


class ConfirmingATrialTerminal(unittest.TestCase):
    def setUp(self):
        self.confirming = ConfirmingTerminals(RECOGNISING)
        self.confirming.try_out(HELPER, TERMINAL)

    def test_waits_while_only_a_shell_runs_in_it(self):
        self.assertEqual(self.confirming.newly_confirmed([with_inside("sh", "/home/sam")]), [])
        self.assertTrue(self.confirming.waiting)

    def test_confirms_once_the_apps_program_runs_in_it_and_stops_waiting(self):
        self.assertEqual(self.confirming.newly_confirmed([with_inside("helper", "/home/sam/code")]), [HELPER])
        self.assertEqual((self.confirming.waiting, self.confirming.confirmed), (False, [HELPER]))

    def test_the_same_program_in_another_window_does_not_count(self):
        elsewhere = window("x", "foot", "", 2, "helper", "/home/sam/code")
        self.assertEqual(self.confirming.newly_confirmed([elsewhere]), [])


if __name__ == "__main__":
    unittest.main()
