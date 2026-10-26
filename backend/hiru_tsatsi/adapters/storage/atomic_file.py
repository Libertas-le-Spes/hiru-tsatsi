import os
import stat
import tempfile
from pathlib import Path
from typing import Callable


class NotWritten(Exception):
    pass


def text_or_nothing(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def write_atomically(path: Path, text: str, read_before: str | None = None,
                     account: Callable[[], int] = os.getuid) -> None:
    target = path.resolve()
    folder = target.parent
    folder.mkdir(parents=True, exist_ok=True)
    if folder.stat().st_uid != account():
        raise NotWritten(f"{folder} belongs to another account, so {path} was left as it was")
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o600
    handle, temporary = tempfile.mkstemp(dir=folder, prefix=f".{target.name}-")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            file.write(text)
            file.flush()
            os.fchmod(file.fileno(), mode)
            os.fsync(file.fileno())
        if read_before is not None and text_or_nothing(target) != read_before:
            raise NotWritten(f"{path} changed while Hiru Tsatsi was writing it, so it was left as it was")
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
    _settle(folder)


def _settle(folder: Path) -> None:
    handle = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(handle)
    finally:
        os.close(handle)
