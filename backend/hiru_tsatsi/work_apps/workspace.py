from dataclasses import dataclass, replace

from hiru_tsatsi.work_apps.app import App


@dataclass(frozen=True)
class Workspace:
    number: int
    label: str
    apps: tuple[App, ...] = ()

    def with_app_added(self, app: App) -> "Workspace":
        return replace(self, apps=self.apps + (app,))

    def with_app_replaced(self, index: int, app: App) -> "Workspace":
        before = self.apps[:index]
        after = self.apps[index + 1:]
        return replace(self, apps=before + (app,) + after)

    def without_app(self, index: int) -> "Workspace":
        before = self.apps[:index]
        after = self.apps[index + 1:]
        return replace(self, apps=before + after)
