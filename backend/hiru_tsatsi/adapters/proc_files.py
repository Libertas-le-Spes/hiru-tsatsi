import os
from pathlib import Path

PROCESS_GROUP_FIELD = 4
FOREGROUND_GROUP_FIELD = 7
START_TIME_FIELD = 21
FIRST_FIELD_AFTER_THE_NAME = 2
TICKS_PER_SECOND = os.sysconf("SC_CLK_TCK")


def _stat_field(stat: str, field: int) -> int | None:
    if ")" not in stat:
        return None
    _, _, after_the_name = stat.rpartition(")")
    fields = after_the_name.split()
    position = field - FIRST_FIELD_AFTER_THE_NAME
    if position >= len(fields):
        return None
    return int(fields[position])


def _group_or_none_found(group: int | None) -> int:
    if group is None:
        return 0
    return group


def real_user_in(status: str) -> int:
    for line in status.splitlines():
        if line.startswith("Uid:"):
            return int(line.split()[1])
    return -1


def process_group_in(stat: str) -> int:
    return _group_or_none_found(_stat_field(stat, PROCESS_GROUP_FIELD))


def foreground_group_in(stat: str) -> int:
    return _group_or_none_found(_stat_field(stat, FOREGROUND_GROUP_FIELD))


def started_in(stat: str) -> float | None:
    ticks = _stat_field(stat, START_TIME_FIELD)
    if ticks is None:
        return None
    return ticks / TICKS_PER_SECOND


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

    def started(self, pid: int) -> float | None:
        return started_in(self._read(pid, "stat"))

    def seconds_since_boot(self) -> float | None:
        try:
            uptime = (self.root / "uptime").read_text()
        except OSError:
            return None
        return float(uptime.split()[0])

    def environment(self, pid: int) -> list[str] | None:
        try:
            raw = (self.root / str(pid) / "environ").read_bytes()
        except FileNotFoundError:
            return []
        except OSError:
            return None
        return raw.decode(errors="replace").split("\0")

    def _read(self, pid: int, name: str) -> str:
        try:
            return (self.root / str(pid) / name).read_text()
        except OSError:
            return ""
