from hiru_tsatsi.work_apps.windows import Window


class FakeNames:
    def __init__(self):
        self.recorded: dict[str, str] = {}

    def record(self, window: Window, name: str) -> None:
        self.recorded[window.address] = name


def namer_installed() -> bool:
    return True
