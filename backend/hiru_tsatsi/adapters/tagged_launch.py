import secrets

from hiru_tsatsi.adapters.proc_files import ProcFiles

TAG = "HIRU_TSATSI_LAUNCH"
TAG_BYTES = 16


class TaggedLaunch:
    def __init__(self, processes: ProcFiles = ProcFiles(), tag: str | None = None):
        if tag is None:
            tag = secrets.token_hex(TAG_BYTES)
        self.processes = processes
        self.entry = f"{TAG}={tag}"

    def tagged(self, command: str) -> str:
        return f"export {self.entry}\n{command}"

    def stopped(self) -> bool:
        pids = self.processes.pids()
        if pids is None:
            return False
        for pid in pids:
            if self.entry in self.processes.environment(pid):
                return False
        return True
