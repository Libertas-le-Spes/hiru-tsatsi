import secrets
from pathlib import Path

TAG = "HIRU_TSATSI_LAUNCH"


def _new_tag() -> str:
    return secrets.token_hex(16)


class TaggedLaunch:
    def __init__(self, processes: Path = Path("/proc"), tag: str | None = None):
        if tag is None:
            tag = _new_tag()
        self.processes = processes
        self.entry = f"{TAG}={tag}"

    def tagged(self, command: str) -> str:
        return f"export {self.entry}\n{command}"

    def stopped(self) -> bool:
        try:
            listed = list(self.processes.iterdir())
        except OSError:
            return False
        for place in listed:
            if place.name.isdigit() and self._carries_tag(place):
                return False
        return True

    def _carries_tag(self, place: Path) -> bool:
        try:
            environment = (place / "environ").read_bytes()
        except OSError:
            return False
        return self.entry.encode() in environment.split(b"\0")
