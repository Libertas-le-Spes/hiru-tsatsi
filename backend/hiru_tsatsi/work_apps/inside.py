import posixpath
import shlex
from dataclasses import dataclass

from hiru_tsatsi.work_apps.windows import Window

THEN = {"&&", ";"}


def _words(command: str) -> list[str]:
    try:
        return list(shlex.shlex(command, posix=True, punctuation_chars=True))
    except ValueError:
        return []


def _goes_to_a_folder_first(words: list[str]) -> bool:
    return len(words) >= 4 and words[0] == "cd" and words[2] in THEN


def _resolved(folder: str, home: str) -> str:
    in_home = folder == "~" or folder.startswith("~/")
    joined = posixpath.join(home, folder[2:]) if in_home else posixpath.join(home, folder)
    return posixpath.normpath(joined)


@dataclass(frozen=True)
class Inside:
    folder: str
    program: str

    @classmethod
    def of(cls, command: str, home: str) -> "Inside | None":
        words = _words(command)
        if not _goes_to_a_folder_first(words):
            return None
        return cls(_resolved(words[1], home), posixpath.basename(words[3]))

    def runs_in(self, window: Window) -> bool:
        return window.program == self.program and window.folder == self.folder


def window_running(command: str, home: str, windows: list[Window], claimed: set[str]) -> Window | None:
    inside = Inside.of(command, home)
    if inside is None:
        return None
    return next((w for w in windows if w.address not in claimed and inside.runs_in(w)), None)
