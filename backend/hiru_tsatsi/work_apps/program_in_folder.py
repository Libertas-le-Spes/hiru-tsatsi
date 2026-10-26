import posixpath
import re
import shlex
from dataclasses import dataclass, replace
from typing import Callable

from hiru_tsatsi.work_apps.shells import SHELLS
from hiru_tsatsi.work_apps.windows import Window

THEN = {"&&", ";"}
LINUX_KEEPS_OF_A_PROGRAM_NAME = 15
RUNS_ANOTHER_PROGRAM = {"env", "exec", "nohup", "setsid", "sudo", "doas", "pkexec", "command", "builtin", "nice",
                        "ionice", "chrt", "taskset", "time", "timeout", "stdbuf", "uwsm", "uwsm-app", "systemd-run",
                        "flatpak", "npx", "pnpx", "bunx", "xargs"}
EXPANDED_BY_THE_SHELL = ("$", "`")
PLAIN_PROGRAM = re.compile(r"[A-Za-z0-9_./+@:,-]+")


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
    if _names_another_users_home(folder):
        return False
    return True


def _names_another_users_home(folder: str) -> bool:
    if not folder.startswith("~"):
        return False
    return folder != "~" and not folder.startswith("~/")


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
        program_word = words[3]
        program = posixpath.basename(program_word)
        if not _folder_is_plain(folder) or not PLAIN_PROGRAM.fullmatch(program_word):
            return None
        if program in RUNS_ANOTHER_PROGRAM or program in SHELLS:
            return None
        return cls(program, _full_folder(folder, home))

    def leading_to(self, real_folder: Callable[[str], str]) -> "ProgramInFolder":
        return replace(self, folder=real_folder(self.folder))

    def runs_in(self, window: Window) -> bool:
        return self._same_program(window) and window.folder == self.folder

    def runs_elsewhere_in(self, window: Window) -> bool:
        return self._same_program(window) and window.folder != self.folder

    def _same_program(self, window: Window) -> bool:
        name_linux_keeps = self.program[:LINUX_KEEPS_OF_A_PROGRAM_NAME]
        return window.program == name_linux_keeps
