import os
from pathlib import Path

PROCESS_GROUP_FIELD = 4
FOREGROUND_GROUP_FIELD = 7
START_TIME_FIELD = 21
TICKS_PER_SECOND = os.sysconf("SC_CLK_TCK")


def _stat_field(stat: str, field: int) -> int:
    name_starts = stat.find("(")
    name_ends = stat.rfind(")")
    if name_starts < 0 or name_ends < 0:
        return 0
    fields = stat[:name_starts].split() + ["name"] + stat[name_ends + 1:].split()
    if len(fields) <= field:
        return 0
    return int(fields[field])


def real_user_in(status: str) -> int:
    for line in status.splitlines():
        if line.startswith("Uid:"):
            return int(line.split()[1])
    return -1


def process_group_in(stat: str) -> int:
    return _stat_field(stat, PROCESS_GROUP_FIELD)


def foreground_group_in(stat: str) -> int:
    return _stat_field(stat, FOREGROUND_GROUP_FIELD)


def started_in(stat: str) -> float:
    return _stat_field(stat, START_TIME_FIELD) / TICKS_PER_SECOND


class ProcFiles:
    def __init__(self, root: Path = Path("/proc")):
        self.root = root

    def own_pids(self, account: int) -> list[int] | None:
        try:
            entries = list(self.root.iterdir())
        except OSError:
            return None
        pids = []
        for entry in entries:
            if entry.name.isdigit() and self._owned_by(entry, account):
                pids.append(int(entry.name))
        return pids

    @staticmethod
    def _owned_by(entry: Path, account: int) -> bool:
        try:
            status = (entry / "status").read_text()
        except OSError:
            return False
        return real_user_in(status) == account

    def program(self, pid: int) -> str:
        return self._read(pid, "comm").strip()

    def folder(self, pid: int) -> str:
        try:
            return str((self.root / str(pid) / "cwd").readlink())
        except OSError:
            return ""

    def children(self, pid: int) -> list[int]:
        children = []
        for child in self._read(pid, f"task/{pid}/children").split():
            children.append(int(child))
        return children

    def process_group(self, pid: int) -> int:
        return process_group_in(self._read(pid, "stat"))

    def foreground_group(self, pid: int) -> int:
        return foreground_group_in(self._read(pid, "stat"))

    def started(self, pid: int) -> float:
        return started_in(self._read(pid, "stat"))

    def seconds_since_boot(self) -> float:
        return float(self._read_file("uptime").split()[0])

    def environment(self, pid: int) -> list[str] | None:
        try:
            raw = (self.root / str(pid) / "environ").read_bytes()
        except FileNotFoundError:
            return []
        except OSError:
            return None
        return raw.decode(errors="replace").split("\0")

    def _read_file(self, name: str) -> str:
        try:
            return (self.root / name).read_text()
        except OSError:
            return "0"

    def _read(self, pid: int, name: str) -> str:
        try:
            return (self.root / str(pid) / name).read_text()
        except OSError:
            return ""
