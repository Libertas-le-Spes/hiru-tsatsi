import time


class SystemClock:
    def now(self) -> float:
        return time.monotonic()

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)
