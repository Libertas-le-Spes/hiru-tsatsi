from pathlib import Path
from typing import Protocol

from hiru_tsatsi.adapters.storage.atomic_file import write_atomically
from hiru_tsatsi.adapters.storage.reading import read_text


class Files(Protocol):
    def read(self, path: Path) -> str: ...

    def exists(self, path: Path) -> bool: ...

    def write(self, path: Path, text: str, read_before: str | None = None, follow_link: bool = False) -> None: ...


class Disk:
    def read(self, path: Path) -> str:
        return read_text(path)

    def exists(self, path: Path) -> bool:
        return path.exists()

    def write(self, path: Path, text: str, read_before: str | None = None, follow_link: bool = False) -> None:
        write_atomically(path, text, read_before, follow_link)
