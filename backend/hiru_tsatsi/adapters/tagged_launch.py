import os
import secrets
from typing import Callable

from hiru_tsatsi.adapters.proc_files import ProcFiles

TAG = "HIRU_TSATSI_LAUNCH"
TAG_BYTES = 16


class TaggedLaunch:
    def __init__(self, processes: ProcFiles, tag: str, account: int):
        self.processes = processes
        self.entry = f"{TAG}={tag}"
        self.account = account
        self.since = processes.seconds_since_boot()

    def wrapped(self, command: str) -> str:
        return f"export {self.entry}\n{command}"

    def stopped(self) -> bool:
        pids = self.processes.own_pids(self.account)
        if pids is None:
            return False
        for pid in pids:
            if self._could_carry_the_tag(pid) and not self._known_not_to_carry_the_tag(pid):
                return False
        return True

    def _could_carry_the_tag(self, pid: int) -> bool:
        return self.processes.started(pid) >= self.since

    def _known_not_to_carry_the_tag(self, pid: int) -> bool:
        environment = self.processes.environment(pid)
        if environment is None:
            return False
        return self.entry not in environment


class TaggedLaunches:
    def __init__(self, processes: ProcFiles, account: Callable[[], int] = os.getuid):
        self.processes = processes
        self.account = account

    def new(self) -> TaggedLaunch:
        return TaggedLaunch(self.processes, secrets.token_hex(TAG_BYTES), self.account())
