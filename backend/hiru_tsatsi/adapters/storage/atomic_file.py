import os
import stat
import tempfile
from pathlib import Path
from typing import Callable

from hiru_tsatsi.adapters.storage.reading import read_text
from hiru_tsatsi.use_cases.failures import ChangedMeanwhile, NotSaved

OWNER_ONLY_FILE = 0o600
OWNER_ONLY_FOLDER = 0o700
WRITABLE_BY_OTHERS = stat.S_IWGRP | stat.S_IWOTH
MOST_LINKS = 40

Account = Callable[[], int]


def write_atomically(path: Path, text: str, read_before: str | None = None, follow_link: bool = False,
                     account: Account = os.getuid) -> None:
    _make_missing_folders(path.parent)
    target = _target(path, follow_link, account)
    folder = target.parent
    _refuse_unsafe_folder(folder, path, account)
    copy = _new_copy(target, text)
    try:
        _refuse_if_changed_meanwhile(target, path, read_before)
        os.replace(copy, target)
    except BaseException:
        copy.unlink(missing_ok=True)
        raise
    _settle(folder)


def _make_missing_folders(folder: Path) -> None:
    missing = []
    while not folder.exists():
        missing.append(folder)
        folder = folder.parent
    for folder in reversed(missing):
        folder.mkdir(mode=OWNER_ONLY_FOLDER)


def _target(path: Path, follow_link: bool, account: Account) -> Path:
    if not follow_link:
        _refuse_a_link(path)
        return path
    _refuse_unsafe_links(path, account)
    return path.resolve()


def _refuse_a_link(path: Path) -> None:
    if path.is_symlink():
        raise NotSaved(f"{path} is a link, and Hiru Tsatsi won't replace a link with a file, so it was left as it was")


def _refuse_unsafe_links(path: Path, account: Account) -> None:
    hop = path
    for _ in range(MOST_LINKS):
        _refuse_unsafe_folder(hop.parent, path, account)
        if not hop.is_symlink():
            return
        hop = hop.parent / hop.readlink()
    raise NotSaved(f"{path} goes through too many links, so it was left as it was")


def _refuse_unsafe_folder(folder: Path, path: Path, account: Account) -> None:
    details = folder.stat()
    if details.st_uid != account():
        raise NotSaved(f"{folder} belongs to another account, so {path} was left as it was")
    if details.st_mode & WRITABLE_BY_OTHERS:
        raise NotSaved(f"other accounts can write to {folder}, so {path} was left as it was")


def _mode_to_keep(target: Path) -> int:
    if not target.exists():
        return OWNER_ONLY_FILE
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
    if read_text(target) != read_before:
        raise ChangedMeanwhile(f"{path} changed while Hiru Tsatsi was writing it, so it was left as it was")


def _settle(folder: Path) -> None:
    handle = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(handle)
    finally:
        os.close(handle)
