import fcntl
import os
from pathlib import Path

from hiru_tsatsi.use_cases.failures import CannotTellIfStarting

OWNER_ONLY = 0o600
OPENING = os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC


class StartLock:
    def __init__(self, path: Path | None, account: int):
        self.path = path
        self.account = account
        self.held: int | None = None

    def claimed(self) -> bool:
        if self.held is not None:
            return True
        lock = self._opened()
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(lock)
            return False
        self.held = lock
        return True

    def _opened(self) -> int:
        if self.path is None:
            raise CannotTellIfStarting("XDG_RUNTIME_DIR is not set")
        try:
            lock = os.open(self.path, OPENING, OWNER_ONLY)
        except OSError as error:
            raise CannotTellIfStarting(f"{self.path} can't be opened ({error.strerror})")
        if os.fstat(lock).st_uid != self.account:
            os.close(lock)
            raise CannotTellIfStarting(f"{self.path} belongs to another account")
        return lock
