import os
import stat
import tempfile
from pathlib import Path
from typing import Callable

from hiru_tsatsi.use_cases.ports import NotSaved

OWNER_ONLY = 0o600
WRITABLE_BY_OTHERS = stat.S_IWGRP | stat.S_IWOTH


def text_or_nothing(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def write_atomically(path: Path, text: str, read_before: str | None = None, follow_link: bool = False,
                     account: Callable[[], int] = os.getuid) -> None:
    target = _target(path, follow_link)
    folder = target.parent
    folder.mkdir(parents=True, exist_ok=True)
    _refuse_unsafe_folder(folder, path, account)
    _refuse_unsafe_folder(path.parent, path, account)
    copy = _new_copy(target, text)
    try:
        _refuse_if_changed_meanwhile(target, path, read_before)
        os.replace(copy, target)
    except BaseException:
        copy.unlink(missing_ok=True)
        raise
    _settle(folder)


def _target(path: Path, follow_link: bool) -> Path:
    if follow_link:
        return path.resolve()
    return path


def _refuse_unsafe_folder(folder: Path, path: Path, account: Callable[[], int]) -> None:
    details = folder.stat()
    if details.st_uid != account():
        raise NotSaved(f"{folder} belongs to another account, so {path} was left as it was")
    if details.st_mode & WRITABLE_BY_OTHERS:
        raise NotSaved(f"other accounts can write to {folder}, so {path} was left as it was")


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
        raise NotSaved(f"{path} changed while Hiru Tsatsi was writing it, so it was left as it was")


def _settle(folder: Path) -> None:
    handle = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(handle)
    finally:
        os.close(handle)
