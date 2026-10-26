from pathlib import Path

SHELLS = {"sh", "dash", "bash", "zsh", "fish"}
FOREGROUND_GROUP_FIELD = 7


class Process:
    def __init__(self, pid: int, processes: Path):
        self.pid = pid
        self.place = processes / str(pid)

    @property
    def program(self) -> str:
        return self._read("comm").strip()

    @property
    def folder(self) -> str:
        try:
            return str((self.place / "cwd").readlink())
        except OSError:
            return ""

    @property
    def is_shell(self) -> bool:
        return self.program in SHELLS

    def first_child(self) -> "Process | None":
        children = self._read(f"task/{self.pid}/children").split()
        if not children:
            return None
        return Process(int(children[0]), self.place.parent)

    def foreground(self) -> "Process":
        group = self._foreground_group()
        if group <= 0:
            return self
        return Process(group, self.place.parent)

    def _foreground_group(self) -> int:
        fields = self._stat_fields()
        if len(fields) <= FOREGROUND_GROUP_FIELD:
            return 0
        return int(fields[FOREGROUND_GROUP_FIELD])

    def _stat_fields(self) -> list[str]:
        stat = self._read("stat")
        name_ends = stat.rfind(")")
        if name_ends < 0:
            return []
        before_name = stat[:stat.find("(")].split()
        after_name = stat[name_ends + 1:].split()
        return before_name + ["name"] + after_name

    def _read(self, name: str) -> str:
        try:
            return (self.place / name).read_text()
        except OSError:
            return ""
