import os
import stat
import tempfile
from pathlib import Path
from typing import Callable

OWNER_ONLY = 0o600


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
    _refuse_another_accounts_folder(folder, path, account)
    copy = _new_copy(target, text)
    try:
        _refuse_if_changed_meanwhile(target, path, read_before)
        os.replace(copy, target)
    except BaseException:
        copy.unlink(missing_ok=True)
        raise
    _settle(folder)


def _refuse_another_accounts_folder(folder: Path, path: Path, account: Callable[[], int]) -> None:
    if folder.stat().st_uid != account():
        raise NotWritten(f"{folder} belongs to another account, so {path} was left as it was")


def _mode_to_keep(target: Path) -> int:
    if not target.exists():
        return OWNER_ONLY
    return stat.S_IMODE(target.stat().st_mode)


def _new_copy(target: Path, text: str) -> Path:
    mode = _mode_to_keep(target)
    handle, name = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}-")
    copy = Path(name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            file.write(text)
            file.flush()
            os.fchmod(file.fileno(), mode)
            os.fsync(file.fileno())
    except BaseException:
        copy.unlink(missing_ok=True)
        raise
    return copy


def _refuse_if_changed_meanwhile(target: Path, path: Path, read_before: str | None) -> None:
    if read_before is None:
        return
    if text_or_nothing(target) != read_before:
        raise NotWritten(f"{path} changed while Hiru Tsatsi was writing it, so it was left as it was")


def _settle(folder: Path) -> None:
    handle = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(handle)
    finally:
        os.close(handle)
