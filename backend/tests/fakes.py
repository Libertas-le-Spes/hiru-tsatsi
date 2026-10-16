from workbench.work_apps.app_list import App, AppList, Workspace
from workbench.work_apps.windows import Window


def window(address: str, window_class: str, title: str = "", workspace: int = 1) -> Window:
    return Window(address, window_class, title, workspace)


def app_list(*spaces: tuple[int, list[App]]) -> AppList:
    return AppList(tuple(Workspace(number, f"Space {number}", tuple(apps)) for number, apps in spaces))


class FakeDesktop:
    def __init__(self, open_now: list[Window], appearing: dict[str, list[Window]] | None = None):
        self.open = list(open_now)
        self.appearing = appearing or {}
        self.launched: list[tuple[str, int]] = []
        self.moves: list[tuple[str, int]] = []

    def windows(self) -> list[Window]:
        return list(self.open)

    def launch(self, command: str, workspace: int) -> None:
        self.launched.append((command, workspace))
        self.open += self.appearing.get(command, [])

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


class FakeNotifier:
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def notify(self, summary: str, body: str) -> None:
        self.sent.append((summary, body))
