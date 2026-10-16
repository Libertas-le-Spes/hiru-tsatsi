import shutil
import subprocess
import time

APP_NAME = "Workbench"
ANSWERS = {"default", "start"}
WAIT_FOR_SERVICE_SECONDS = 60
RETRY_SECONDS = 2


class NotifySend:
    def notify(self, summary: str, body: str) -> None:
        if shutil.which("notify-send"):
            subprocess.run(["notify-send", "-a", APP_NAME, summary, body], check=False)

    def ask(self, summary: str, body: str, action: str) -> bool:
        if not shutil.which("notify-send"):
            return False
        question = ["notify-send", "-a", APP_NAME, "--urgency=critical", f"--action=default={action}",
                    f"--action=start={action}", summary, body]
        deadline = time.monotonic() + WAIT_FOR_SERVICE_SECONDS
        answered = subprocess.run(question, capture_output=True, text=True, check=False)
        while answered.returncode != 0 and time.monotonic() < deadline:
            time.sleep(RETRY_SECONDS)
            answered = subprocess.run(question, capture_output=True, text=True, check=False)
        return answered.stdout.strip() in ANSWERS
