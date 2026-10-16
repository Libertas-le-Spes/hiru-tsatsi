import subprocess
from typing import Mapping

from workbench.work_apps.windows import Window


class LaunchOnly:
    sees_windows = False

    @classmethod
    def found(cls, env: Mapping[str, str]) -> "LaunchOnly":
        return cls()

    def windows(self) -> list[Window]:
        return []

    def launch(self, command: str, workspace: int) -> None:
        subprocess.Popen(["sh", "-c", command], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)

    def move(self, window: Window, workspace: int) -> None:
        return None
