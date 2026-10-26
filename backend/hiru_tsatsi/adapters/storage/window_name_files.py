import re
from pathlib import Path

from hiru_tsatsi.adapters.storage.files import Files
from hiru_tsatsi.work_apps.windows import Window

WINDOW_ADDRESS = re.compile(r"0x[0-9a-f]+")


class WindowNameFiles:
    def __init__(self, folder: Path, files: Files):
        self.folder = folder
        self.files = files

    def record(self, window: Window, name: str) -> None:
        if not WINDOW_ADDRESS.fullmatch(window.address):
            return
        self.files.write(self.folder / window.address, name + "\n")
