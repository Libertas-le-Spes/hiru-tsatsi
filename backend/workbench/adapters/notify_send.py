import shutil
import subprocess

APP_NAME = "Workbench"


class NotifySend:
    def notify(self, summary: str, body: str) -> None:
        if shutil.which("notify-send"):
            subprocess.run(["notify-send", "-a", APP_NAME, summary, body], check=False)
