from pathlib import Path
from typing import Protocol

from hiru_tsatsi.adapters.storage.atomic_file import NotWritten, write_atomically
from hiru_tsatsi.use_cases.ports import NotSaved


class Files(Protocol):
    def read(self, path: Path) -> str: ...

    def exists(self, path: Path) -> bool: ...

    def write(self, path: Path, text: str, read_before: str | None = None) -> None: ...


class Disk:
    def read(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def exists(self, path: Path) -> bool:
        return path.exists()

    def write(self, path: Path, text: str, read_before: str | None = None) -> None:
        try:
            write_atomically(path, text, read_before)
        except NotWritten as refused:
            raise NotSaved(str(refused)) from refused
