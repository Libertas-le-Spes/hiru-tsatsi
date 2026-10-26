import posixpath
import shlex
from dataclasses import dataclass

from hiru_tsatsi.work_apps.windows import Window

THEN = {"&&", ";"}
RUNS_ANOTHER_PROGRAM = {"env", "exec", "nohup", "setsid", "sudo", "doas", "command", "nice", "time", "uwsm-app"}
EXPANDED_BY_THE_SHELL = ("$", "`")


def _words(command: str) -> list[str]:
    splitter = shlex.shlex(command, posix=True, punctuation_chars=True)
    try:
        return list(splitter)
    except ValueError:
        return []


def _goes_to_a_folder_first(words: list[str]) -> bool:
    if len(words) < 4:
        return False
    return words[0] == "cd" and words[2] in THEN


def _folder_is_plain(folder: str) -> bool:
    for sign in EXPANDED_BY_THE_SHELL:
        if sign in folder:
            return False
    if folder.startswith("~") and folder != "~" and not folder.startswith("~/"):
        return False
    return True


def _full_folder(folder: str, home: str) -> str:
    if folder == "~":
        return home
    if folder.startswith("~/"):
        folder = folder.removeprefix("~/")
    return posixpath.normpath(posixpath.join(home, folder))


@dataclass(frozen=True)
class ProgramInFolder:
    program: str
    folder: str

    @classmethod
    def of(cls, command: str, home: str) -> "ProgramInFolder | None":
        words = _words(command)
        if not _goes_to_a_folder_first(words):
            return None
        folder = words[1]
        program = posixpath.basename(words[3])
        if not _folder_is_plain(folder) or program in RUNS_ANOTHER_PROGRAM:
            return None
        return cls(program, _full_folder(folder, home))

    def runs_in(self, window: Window) -> bool:
        return window.program == self.program and window.folder == self.folder
