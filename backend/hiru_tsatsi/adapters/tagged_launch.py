import secrets
from pathlib import Path

TAG = "HIRU_TSATSI_LAUNCH"


class TaggedLaunch:
    def __init__(self, processes: Path = Path("/proc"), tag: str | None = None):
        self.processes = processes
        self.entry = f"{TAG}={tag or secrets.token_hex(16)}"

    def tagged(self, command: str) -> str:
        return f"export {self.entry}\n{command}"

    def stopped(self) -> bool:
        try:
            running = [process for process in self.processes.iterdir() if process.name.isdigit()]
        except OSError:
            return False
        return not any(self._carries_tag(process) for process in running)

    def _carries_tag(self, process: Path) -> bool:
        try:
            return self.entry.encode() in (process / "environ").read_bytes().split(b"\0")
        except OSError:
            return False
