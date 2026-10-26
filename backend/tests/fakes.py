from hiru_tsatsi.work_apps.app_list import App, AppList, Workspace
from hiru_tsatsi.work_apps.shortcut import Keys
from hiru_tsatsi.work_apps.windows import Window


HOME = "/home/sam"


def window(address: str, window_class: str, title: str = "", workspace: int = 1, program: str = "", folder: str = "") -> Window:
    return Window(address, window_class, title, workspace, program, folder)


def app_list(*spaces: tuple[int, list[App]]) -> AppList:
    return AppList(tuple(Workspace(number, f"Space {number}", tuple(apps)) for number, apps in spaces))


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
        self.stopping = stopping or set()
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


class FakeStore:
    def __init__(self, apps: AppList):
        self.apps = apps
        self.saves = 0

    def load(self) -> AppList:
        return self.apps

    def save(self, apps: AppList) -> None:
        self.apps = apps
        self.saves += 1


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def wait(self, seconds: float) -> None:
        self.now += seconds


class FakeNames:
    def __init__(self):
        self.recorded: dict[str, str] = {}

    def record(self, window: Window, name: str) -> None:
        self.recorded[window.address] = name


class FakeSettings:
    def __init__(self, window_titles: bool | None = None):
        self.titles = window_titles

    def window_titles(self) -> bool | None:
        return self.titles

    def set_window_titles(self, on: bool) -> None:
        self.titles = on


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


class FakeSetUp:
    def __init__(self, taken: set[Keys] | None = None, installed: Keys | None = None):
        self.taken = taken or set()
        self.installed = installed
        self.installs: list[tuple[Keys | None, str, str]] = []

    def installed_keys(self) -> Keys | None:
        return self.installed

    def taken_keys(self) -> set[Keys]:
        return self.taken

    def install(self, keys: Keys | None, start_command: str, ask_command: str) -> None:
        self.installs.append((keys, start_command, ask_command))
