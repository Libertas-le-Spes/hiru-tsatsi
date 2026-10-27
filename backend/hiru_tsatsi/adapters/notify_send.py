import shutil
import subprocess
import time

from hiru_tsatsi.use_cases.ports import Answer

APP_NAME = "Hiru Tsatsi"
ANSWERS = {"default", "start"}
NEVER = "never"
WAIT_FOR_SERVICE_SECONDS = 60
RETRY_SECONDS = 2


def _question(summary: str, body: str, action: str, *asking_for: str) -> list[str]:
    return ["notify-send", "-a", APP_NAME, "--urgency=critical", *asking_for, f"--action=default={action}",
            f"--action=start={action}", "--", summary, body]


def _question_with_a_no(summary: str, body: str, action: str, decline: str) -> list[str]:
    return _question(summary, body, action, "--print-id", f"--action={NEVER}={decline}")


def _line(printed: str, number: int) -> str:
    lines = printed.splitlines()
    if len(lines) <= number:
        return ""
    return lines[number].strip()


def _answer(clicked: str) -> Answer:
    if clicked in ANSWERS:
        return Answer.YES
    if clicked == NEVER:
        return Answer.NO
    return Answer.NOT_ANSWERED


def _close(shown: str) -> None:
    if not shown.isdigit() or not shutil.which("gdbus"):
        return
    subprocess.run(["gdbus", "call", "--session", "--dest", "org.freedesktop.Notifications",
                    "--object-path", "/org/freedesktop/Notifications",
                    "--method", "org.freedesktop.Notifications.CloseNotification", shown],
                   capture_output=True, check=False)


class NotifySend:
    def notify(self, summary: str, body: str) -> None:
        if shutil.which("notify-send"):
            subprocess.run(["notify-send", "-a", APP_NAME, "--", summary, body], check=False)

    def ask(self, summary: str, body: str, action: str) -> bool:
        if not shutil.which("notify-send"):
            return False
        question = _question(summary, body, action)
        deadline = time.monotonic() + WAIT_FOR_SERVICE_SECONDS
        answered = subprocess.run(question, capture_output=True, text=True, check=False)
        while answered.returncode != 0 and time.monotonic() < deadline:
            time.sleep(RETRY_SECONDS)
            answered = subprocess.run(question, capture_output=True, text=True, check=False)
        return answered.stdout.strip() in ANSWERS

    def ask_within(self, summary: str, body: str, action: str, decline: str, seconds: float) -> Answer:
        if not shutil.which("notify-send"):
            return Answer.NOT_ANSWERED
        question = _question_with_a_no(summary, body, action, decline)
        asking = subprocess.Popen(question, stdout=subprocess.PIPE, text=True)
        try:
            printed, _ = asking.communicate(timeout=seconds)
        except subprocess.TimeoutExpired:
            asking.kill()
            printed, _ = asking.communicate()
            _close(_line(printed, 0))
        return _answer(_line(printed, 1))
