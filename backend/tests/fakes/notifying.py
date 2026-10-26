class FakeAnnouncer:
    def __init__(self):
        self.announced: list[list[str]] = []

    def announce(self, starting: list[str]) -> None:
        self.announced.append(starting)


class FakeNotifier:
    def __init__(self, clicks: bool = False):
        self.sent: list[tuple[str, str]] = []
        self.clicks = clicks
        self.asked: list[str] = []

    def notify(self, summary: str, body: str) -> None:
        self.sent.append((summary, body))

    def ask(self, summary: str, body: str, action: str) -> bool:
        self.asked.append(summary)
        return self.clicks
