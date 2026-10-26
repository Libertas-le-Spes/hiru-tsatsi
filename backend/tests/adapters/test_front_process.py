import unittest

from tests.adapters.mocked_processes import Running, processes_running
from hiru_tsatsi.adapters.front_process import FrontProcess


def front_of(pid: int, running: dict[int, Running]) -> tuple[str, str]:
    return FrontProcess(processes_running(running)).of_window(pid)


class FindingWhatRunsInAWindow(unittest.TestCase):
    def test_the_program_a_shell_handed_the_terminal_to(self):
        running = {10: Running("foot", children=[11]), 11: Running("bash", children=[12], front=12),
                   12: Running("helper", "/home/sam/code", children=[13]), 13: Running("bash", "/home/sam/code")}
        self.assertEqual(front_of(10, running), ("helper", "/home/sam/code"))

    def test_the_program_behind_shells_that_only_wait_for_it(self):
        running = {20: Running("foot", children=[21]), 21: Running("sh", children=[22], front=21, group=21),
                   22: Running("sh", "/home/sam/code", children=[23], front=21, group=21),
                   23: Running("helper", "/home/sam/code", front=21, group=21)}
        self.assertEqual(front_of(20, running), ("helper", "/home/sam/code"))

    def test_a_program_running_a_tool_of_its_own_is_still_what_runs(self):
        running = {80: Running("foot", children=[81]), 81: Running("bash", children=[82], front=82, group=81),
                   82: Running("helper", "/home/sam/code", children=[83], front=82, group=82),
                   83: Running("grep", "/home/sam/code", front=82, group=82)}
        self.assertEqual(front_of(80, running), ("helper", "/home/sam/code"))

    def test_a_shell_waiting_for_typing_is_what_runs(self):
        running = {30: Running("foot", children=[31]), 31: Running("bash", "/home/sam/code", front=31)}
        self.assertEqual(front_of(30, running), ("bash", "/home/sam/code"))

    def test_a_program_with_several_children_says_nothing_rather_than_guess(self):
        running = {50: Running("kitty", children=[51, 52]), 51: Running("helper", "/home/sam/code"),
                   52: Running("bash", "/home/sam/other")}
        self.assertEqual(front_of(50, running), ("", ""))

    def test_a_window_with_nothing_started_inside_runs_nothing_known(self):
        self.assertEqual(front_of(40, {40: Running("chromium")}), ("", ""))

    def test_a_shell_with_one_background_job_is_what_runs_not_the_job(self):
        running = {60: Running("foot", children=[61]),
                   61: Running("bash", "/home/sam/code", children=[62], front=61, group=61),
                   62: Running("helper", "/home/sam/code", front=61, group=62)}
        self.assertEqual(front_of(60, running), ("bash", "/home/sam/code"))

    def test_a_child_whose_group_cannot_be_read_is_never_taken_for_what_runs(self):
        running = {70: Running("foot", children=[71]), 71: Running("bash", "/home/sam/code", children=[72], front=71),
                   72: Running("helper", "/home/sam/code")}
        self.assertEqual(front_of(70, running), ("bash", "/home/sam/code"))


if __name__ == "__main__":
    unittest.main()
