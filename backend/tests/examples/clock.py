class TickingClock:
    def __init__(self):
        self.seconds = 0.0

    def now(self) -> float:
        return self.seconds

    def wait(self, seconds: float) -> None:
        self.seconds += seconds
