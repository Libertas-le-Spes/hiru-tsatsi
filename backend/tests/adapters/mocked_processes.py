from dataclasses import dataclass, field
from unittest.mock import Mock, create_autospec

from hiru_tsatsi.adapters.proc_files import ProcFiles


@dataclass(frozen=True)
class Running:
    program: str
    folder: str = "/home/sam"
    children: list[int] = field(default_factory=list)
    front: int = 0
    environment: list[str] | None = field(default_factory=list)
    started: float = 100.0


NOTHING = Running("", "")


class Table:
    def __init__(self, running: dict[int, Running]):
        self.running = running

    def of(self, pid: int) -> Running:
        return self.running.get(pid, NOTHING)

    def program(self, pid: int) -> str:
        return self.of(pid).program

    def folder(self, pid: int) -> str:
        return self.of(pid).folder

    def children(self, pid: int) -> list[int]:
        return self.of(pid).children

    def foreground_group(self, pid: int) -> int:
        return self.of(pid).front

    def environment(self, pid: int) -> list[str] | None:
        return self.of(pid).environment

    def started(self, pid: int) -> float:
        return self.of(pid).started


def processes_running(running: dict[int, Running]) -> Mock:
    table = Table(running)
    processes = create_autospec(ProcFiles, instance=True)
    processes.own_pids.return_value = list(running)
    processes.seconds_since_boot.return_value = 100.0
    processes.program.side_effect = table.program
    processes.folder.side_effect = table.folder
    processes.children.side_effect = table.children
    processes.foreground_group.side_effect = table.foreground_group
    processes.environment.side_effect = table.environment
    processes.started.side_effect = table.started
    return processes
