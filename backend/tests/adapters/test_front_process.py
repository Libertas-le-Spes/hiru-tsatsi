import tempfile
import unittest
from pathlib import Path

from hiru_tsatsi.adapters.front_process import FrontProcess


class Processes:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp())

    def add(self, pid: int, program: str, folder: str, children: list[int], front: int = 0) -> None:
        place = self.root / str(pid)
        (place / "task" / str(pid)).mkdir(parents=True)
        (place / "comm").write_text(program + "\n")
        (place / "task" / str(pid) / "children").write_text(" ".join(str(child) for child in children))
        (place / "stat").write_text(f"{pid} ({program}) S 1 {pid} {pid} 34816 {front} 0")
        (place / "cwd").symlink_to(folder)


class FindingWhatRunsInAWindow(unittest.TestCase):
    def setUp(self):
        self.processes = Processes()

    def front_of(self, pid: int) -> tuple[str, str]:
        return FrontProcess(self.processes.root).of_window(pid)

    def test_the_program_a_shell_handed_the_terminal_to(self):
        self.processes.add(10, "foot", "/home/sam", [11])
        self.processes.add(11, "bash", "/home/sam", [12], front=12)
        self.processes.add(12, "helper", "/home/sam/code", [13])
        self.processes.add(13, "bash", "/home/sam/code", [])
        self.assertEqual(self.front_of(10), ("helper", "/home/sam/code"))

    def test_the_program_behind_shells_that_only_wait_for_it(self):
        self.processes.add(20, "foot", "/home/sam", [21])
        self.processes.add(21, "sh", "/home/sam", [22], front=21)
        self.processes.add(22, "sh", "/home/sam/code", [23])
        self.processes.add(23, "helper", "/home/sam/code", [])
        self.assertEqual(self.front_of(20), ("helper", "/home/sam/code"))

    def test_a_shell_waiting_for_typing_is_what_runs(self):
        self.processes.add(30, "foot", "/home/sam", [31])
        self.processes.add(31, "bash", "/home/sam/code", [], front=31)
        self.assertEqual(self.front_of(30), ("bash", "/home/sam/code"))

    def test_a_window_whose_processes_cannot_be_read_runs_nothing_known(self):
        self.assertEqual(self.front_of(40), ("", ""))


if __name__ == "__main__":
    unittest.main()
