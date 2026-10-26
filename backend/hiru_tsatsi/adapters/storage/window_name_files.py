import re
from pathlib import Path

from hiru_tsatsi.adapters.storage.files import Disk, Files
from hiru_tsatsi.work_apps.windows import Window

SAFE_ADDRESS = re.compile(r"[\w.-]+")


class WindowNameFiles:
    def __init__(self, folder: Path, files: Files = Disk()):
        self.folder = folder
        self.files = files

    def record(self, window: Window, name: str) -> None:
        if not SAFE_ADDRESS.fullmatch(window.address):
            return
        self.files.write(self.folder / window.address, name + "\n")
