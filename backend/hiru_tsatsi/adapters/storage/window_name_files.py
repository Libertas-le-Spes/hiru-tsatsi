import os
import re
import tempfile
from pathlib import Path

from hiru_tsatsi.work_apps.windows import Window

SAFE_ADDRESS = re.compile(r"[\w.-]+")


class WindowNameFiles:
    def __init__(self, folder: Path):
        self.folder = folder

    def record(self, window: Window, name: str) -> None:
        if not SAFE_ADDRESS.fullmatch(window.address):
            return
        self.folder.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(dir=self.folder, prefix=".writing-")
        with os.fdopen(handle, "w") as file:
            file.write(name + "\n")
        os.replace(temporary, self.folder / window.address)
