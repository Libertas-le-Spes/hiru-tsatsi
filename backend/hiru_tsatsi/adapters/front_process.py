from pathlib import Path

from hiru_tsatsi.adapters.process import Process

DEEPEST = 8


class FrontProcess:
    def __init__(self, processes: Path = Path("/proc")):
        self.processes = processes

    def of_window(self, pid: int) -> tuple[str, str]:
        shell = Process(pid, self.processes).first_child()
        if shell is None:
            return "", ""
        front = self._past_waiting_shells(shell.foreground())
        return front.program, front.folder

    @staticmethod
    def _past_waiting_shells(process: Process) -> Process:
        for _ in range(DEEPEST):
            child = process.first_child()
            if not process.is_shell or child is None:
                return process
            process = child
        return process
