from dataclasses import dataclass, replace


@dataclass(frozen=True)
class App:
    name: str
    command: str
    window: str = ""

    @property
    def named(self) -> bool:
        return self.window.strip() != ""


@dataclass(frozen=True)
class Workspace:
    number: int
    label: str
    apps: tuple[App, ...] = ()


@dataclass(frozen=True)
class Placement:
    workspace: int
    index: int
    app: App


@dataclass(frozen=True)
class AppList:
    workspaces: tuple[Workspace, ...] = ()

    def placements(self) -> list[Placement]:
        return [Placement(space.number, index, app) for space in self.workspaces for index, app in enumerate(space.apps)]

    def with_window(self, placement: Placement, window: str) -> "AppList":
        return AppList(tuple(self._space_with_window(space, placement, window) for space in self.workspaces))

    @staticmethod
    def _space_with_window(space: Workspace, placement: Placement, window: str) -> Workspace:
        if space.number != placement.workspace:
            return space
        apps = tuple(replace(app, window=window) if index == placement.index else app for index, app in enumerate(space.apps))
        return replace(space, apps=apps)
