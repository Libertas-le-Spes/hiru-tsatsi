import unittest
from unittest.mock import Mock, create_autospec

from tests.examples.windows import window
from hiru_tsatsi.adapters.seeing_inside import SeeingInside
from hiru_tsatsi.use_cases.ports import Desktop
from hiru_tsatsi.work_apps.windows import Window


def desktop_with(windows: list[Window]) -> Mock:
    desktop = create_autospec(Desktop, instance=True)
    desktop.windows.return_value = windows
    return desktop


def helper_in_code(pid: int) -> tuple[str, str]:
    return "helper", "/home/sam/code"


class LookingInsideWindows(unittest.TestCase):
    def test_each_window_with_its_own_program_says_what_runs_inside(self):
        seeing = SeeingInside(desktop_with([Window("0xb", "foot", "t", 2, pid=77)]), helper_in_code)
        seen = seeing.windows()[0]
        self.assertEqual((seen.program, seen.folder), ("helper", "/home/sam/code"))

    def test_windows_that_share_one_program_say_nothing_rather_than_guess(self):
        shared = [Window("0xa", "kitty", "a", 1, pid=77), Window("0xb", "kitty", "b", 2, pid=77)]
        what_runs = Mock(side_effect=helper_in_code)
        for seen in SeeingInside(desktop_with(shared), what_runs).windows():
            self.assertEqual((seen.program, seen.folder), ("", ""))
        what_runs.assert_not_called()

    def test_a_window_without_a_known_program_says_nothing(self):
        what_runs = Mock(side_effect=helper_in_code)
        seen = SeeingInside(desktop_with([Window("0xc", "steam", "Steam", 6, pid=0)]), what_runs).windows()[0]
        self.assertEqual((seen.program, seen.folder), ("", ""))
        what_runs.assert_not_called()

    def test_launching_and_moving_go_straight_to_the_desktop(self):
        desktop = desktop_with([])
        steam = window("0xa", "steam")
        seeing = SeeingInside(desktop, helper_in_code)
        seeing.launch("steam", 6)
        seeing.move(steam, 6)
        desktop.launch.assert_called_once_with("steam", 6)
        desktop.move.assert_called_once_with(steam, 6)


if __name__ == "__main__":
    unittest.main()
