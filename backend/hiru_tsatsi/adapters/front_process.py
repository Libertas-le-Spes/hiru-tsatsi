from pathlib import Path

NOTHING = ("", "")
SHELLS = {"sh", "dash", "bash", "zsh", "fish"}
DEEPEST = 8


class FrontProcess:
    def __init__(self, processes: Path = Path("/proc")):
        self.processes = processes

    def of_window(self, pid: int) -> tuple[str, str]:
        shell = self._first_child(pid)
        if shell is None:
            return NOTHING
        front = self._past_waiting_shells(self._foreground_group(shell) or shell)
        return self._program(front), self._folder(front)

    def _past_waiting_shells(self, pid: int) -> int:
        for _ in range(DEEPEST):
            child = self._first_child(pid)
            if self._program(pid) not in SHELLS or child is None:
                return pid
            pid = child
        return pid

    def _program(self, pid: int) -> str:
        return self._read(pid, "comm").strip()

    def _first_child(self, pid: int) -> int | None:
        children = self._read(pid, f"task/{pid}/children").split()
        return int(children[0]) if children else None

    def _foreground_group(self, pid: int) -> int | None:
        stat = self._read(pid, "stat")
        after_name = stat[stat.rfind(")") + 2:].split()
        group = int(after_name[5]) if len(after_name) > 5 else 0
        return group if group > 0 else None

    def _folder(self, pid: int) -> str:
        try:
            return str((self.processes / str(pid) / "cwd").readlink())
        except OSError:
            return ""

    def _read(self, pid: int, name: str) -> str:
        try:
            return (self.processes / str(pid) / name).read_text()
        except OSError:
            return ""
