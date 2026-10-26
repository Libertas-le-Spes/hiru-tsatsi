from pathlib import Path
from typing import Protocol

from hiru_tsatsi.adapters.storage.atomic_file import write_atomically
from hiru_tsatsi.use_cases.ports import NotReadable


class Files(Protocol):
    def read(self, path: Path) -> str: ...

    def exists(self, path: Path) -> bool: ...

    def write(self, path: Path, text: str, read_before: str | None = None, follow_link: bool = False) -> None: ...


class Disk:
    def read(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ""
        except (OSError, UnicodeDecodeError) as unreadable:
            raise NotReadable(f"{path} could not be read ({unreadable})") from unreadable

    def exists(self, path: Path) -> bool:
        return path.exists()

    def write(self, path: Path, text: str, read_before: str | None = None, follow_link: bool = False) -> None:
        write_atomically(path, text, read_before, follow_link)
