from pathlib import Path
from typing import Protocol

from hiru_tsatsi.adapters.storage.atomic_file import write_atomically


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
        write_atomically(path, text, read_before)
