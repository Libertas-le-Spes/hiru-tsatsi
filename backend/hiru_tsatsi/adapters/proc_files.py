from pathlib import Path

FOREGROUND_GROUP_FIELD = 7


def foreground_group_in(stat: str) -> int:
    name_starts = stat.find("(")
    name_ends = stat.rfind(")")
    if name_starts < 0 or name_ends < 0:
        return 0
    fields = stat[:name_starts].split() + ["name"] + stat[name_ends + 1:].split()
    if len(fields) <= FOREGROUND_GROUP_FIELD:
        return 0
    return int(fields[FOREGROUND_GROUP_FIELD])


class ProcFiles:
    def __init__(self, root: Path = Path("/proc")):
        self.root = root

    def pids(self) -> list[int] | None:
        try:
            entries = list(self.root.iterdir())
        except OSError:
            return None
        pids = []
        for entry in entries:
            if entry.name.isdigit():
                pids.append(int(entry.name))
        return pids

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

    def foreground_group(self, pid: int) -> int:
        return foreground_group_in(self._read(pid, "stat"))

    def environment(self, pid: int) -> list[str]:
        try:
            raw = (self.root / str(pid) / "environ").read_bytes()
        except OSError:
            return []
        return raw.decode(errors="replace").split("\0")

    def _read(self, pid: int, name: str) -> str:
        try:
            return (self.root / str(pid) / name).read_text()
        except OSError:
            return ""
