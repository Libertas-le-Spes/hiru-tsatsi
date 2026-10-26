import posixpath
import shlex
from dataclasses import dataclass

from hiru_tsatsi.work_apps.windows import Window

THEN = {"&&", ";"}


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
        program = words[3]
        return cls(posixpath.basename(program), _full_folder(folder, home))

    def runs_in(self, window: Window) -> bool:
        return window.program == self.program and window.folder == self.folder
