from hiru_tsatsi.use_cases.ports import Notifier


def _how_many(count: int) -> str:
    if count == 1:
        return "1 work app"
    return f"{count} work apps"


class StartingNotice:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier

    def announce(self, starting: list[str]) -> None:
        self.notifier.notify(f"Starting {_how_many(len(starting))}", ", ".join(starting))
