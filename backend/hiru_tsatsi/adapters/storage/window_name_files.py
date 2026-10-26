import re
from pathlib import Path

from hiru_tsatsi.adapters.storage.atomic_file import write_atomically

from hiru_tsatsi.work_apps.windows import Window

SAFE_ADDRESS = re.compile(r"[\w.-]+")


class WindowNameFiles:
    def __init__(self, folder: Path):
        self.folder = folder

    def record(self, window: Window, name: str) -> None:
        if not SAFE_ADDRESS.fullmatch(window.address):
            return
        write_atomically(self.folder / window.address, name + "\n")
