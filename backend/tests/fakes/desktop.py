from hiru_tsatsi.work_apps.windows import Window


def window(address: str, window_class: str, title: str = "", workspace: int = 1, program: str = "", folder: str = "") -> Window:
    return Window(address, window_class, title, workspace, program, folder)


class FakeLaunch:
    def __init__(self, stopped: bool):
        self.has_stopped = stopped

    def stopped(self) -> bool:
        return self.has_stopped


class FakeDesktop:
    def __init__(self, open_now: list[Window], appearing: dict[str, list[Window]] | None = None,
                 stopping: set[str] | None = None):
        self.open = list(open_now)
        self.appearing = appearing or {}
        if stopping is None:
            stopping = set()
        self.stopping = stopping
        self.launched: list[tuple[str, int]] = []
        self.in_terminal: list[tuple[str, int, str]] = []
        self.moves: list[tuple[str, int]] = []

    def windows(self) -> list[Window]:
        return list(self.open)

    def launch(self, command: str, workspace: int) -> FakeLaunch:
        self.launched.append((command, workspace))
        self.open += self.appearing.get(command, [])
        return FakeLaunch(command in self.stopping)

    def launch_in_terminal(self, command: str, workspace: int, window: str) -> None:
        self.in_terminal.append((command, workspace, window))
        self.open.append(Window(f"terminal-{window}", window, "foot", workspace))

    def move(self, window: Window, workspace: int) -> None:
        self.moves.append((window.address, workspace))
