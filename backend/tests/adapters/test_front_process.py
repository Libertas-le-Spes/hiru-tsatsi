import tempfile
import unittest
from pathlib import Path

from hiru_tsatsi.adapters.front_process import FrontProcess


class Processes:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp())

    def add(self, pid: int, program: str, folder: str, children: list[int] = (), front: int = 0) -> "Processes":
        place = self.root / str(pid)
        (place / "task" / str(pid)).mkdir(parents=True)
        (place / "comm").write_text(program + "\n")
        (place / "task" / str(pid) / "children").write_text(" ".join(map(str, children)))
        (place / "stat").write_text(f"{pid} ({program}) S 1 {pid} {pid} 34816 {front} 0")
        (place / "cwd").symlink_to(folder)
        return self


class FindingWhatRunsInAWindow(unittest.TestCase):
    def test_the_program_a_shell_handed_the_terminal_to(self):
        processes = Processes().add(10, "foot", "/home/sam", [11]).add(11, "bash", "/home/sam", [12], front=12) \
            .add(12, "helper", "/home/sam/code/harbour", [13]).add(13, "bash", "/home/sam/code/harbour")
        self.assertEqual(FrontProcess(processes.root).of_window(10), ("helper", "/home/sam/code/harbour"))

    def test_the_program_behind_shells_that_only_wait_for_it(self):
        processes = Processes().add(20, "foot", "/home/sam", [21]).add(21, "sh", "/home/sam", [22], front=21) \
            .add(22, "sh", "/home/sam/code/harbour", [23]).add(23, "helper", "/home/sam/code/harbour")
        self.assertEqual(FrontProcess(processes.root).of_window(20), ("helper", "/home/sam/code/harbour"))

    def test_a_shell_waiting_for_typing_is_what_runs(self):
        processes = Processes().add(30, "foot", "/home/sam", [31]).add(31, "bash", "/home/sam/code", front=31)
        self.assertEqual(FrontProcess(processes.root).of_window(30), ("bash", "/home/sam/code"))

    def test_a_window_whose_processes_cannot_be_read_runs_nothing_known(self):
        self.assertEqual(FrontProcess(Processes().root).of_window(40), ("", ""))


if __name__ == "__main__":
    unittest.main()
