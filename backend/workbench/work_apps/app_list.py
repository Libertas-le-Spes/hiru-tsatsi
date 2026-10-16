from dataclasses import dataclass, replace


class Refused(Exception):
    pass


class NumberTaken(Refused):
    def __init__(self, number: int):
        super().__init__(number)
        self.number = number


class NothingThere(Refused):
    pass


class Blank(Refused):
    def __init__(self, field: str):
        super().__init__(field)
        self.field = field


@dataclass(frozen=True)
class App:
    name: str
    command: str
    learned_window: str = ""

    @property
    def knows_window(self) -> bool:
        return self.learned_window.strip() != ""


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


def _required(field: str, value: str) -> str:
    if not value.strip():
        raise Blank(field)
    return value.strip()


@dataclass(frozen=True)
class AppList:
    workspaces: tuple[Workspace, ...] = ()

    def placements(self) -> list[Placement]:
        return [Placement(space.number, index, app) for space in self.workspaces for index, app in enumerate(space.apps)]

    def placement(self, workspace: int, index: int) -> Placement:
        apps = self.workspace(workspace).apps
        if not 0 <= index < len(apps):
            raise NothingThere()
        return Placement(workspace, index, apps[index])

    def workspace(self, number: int) -> Workspace:
        found = next((space for space in self.workspaces if space.number == number), None)
        if found is None:
            raise NothingThere()
        return found

    def has_workspace(self, number: int) -> bool:
        return any(space.number == number for space in self.workspaces)

    def next_free_number(self) -> int:
        return max((space.number for space in self.workspaces), default=0) + 1

    def with_workspace(self, number: int, label: str) -> "AppList":
        if number < 1 or self.has_workspace(number):
            raise NumberTaken(number)
        return self._sorted(self.workspaces + (Workspace(number, _required("label", label)),))

    def with_workspace_changed(self, number: int, new_number: int, label: str) -> "AppList":
        space = self.workspace(number)
        if new_number != number and (new_number < 1 or self.has_workspace(new_number)):
            raise NumberTaken(new_number)
        changed = replace(space, number=new_number, label=_required("label", label))
        return self._sorted(tuple(changed if s.number == number else s for s in self.workspaces))

    def without_workspace(self, number: int) -> "AppList":
        self.workspace(number)
        return AppList(tuple(space for space in self.workspaces if space.number != number))

    def with_app(self, workspace: int, app: App) -> "AppList":
        checked = App(_required("name", app.name), _required("command", app.command), app.learned_window)
        return self._with_apps(workspace, lambda apps: apps + (checked,))

    def with_app_changed(self, workspace: int, index: int, name: str, command: str) -> "AppList":
        current = self.placement(workspace, index).app
        changed = replace(current, name=_required("name", name), command=_required("command", command))
        return self._with_apps(workspace, lambda apps: apps[:index] + (changed,) + apps[index + 1:])

    def without_app(self, workspace: int, index: int) -> "AppList":
        self.placement(workspace, index)
        return self._with_apps(workspace, lambda apps: apps[:index] + apps[index + 1:])

    def with_learned_window(self, placement: Placement, window: str) -> "AppList":
        changed = replace(self.placement(placement.workspace, placement.index).app, learned_window=window)
        index = placement.index
        return self._with_apps(placement.workspace, lambda apps: apps[:index] + (changed,) + apps[index + 1:])

    def _with_apps(self, workspace: int, change) -> "AppList":
        space = self.workspace(workspace)
        changed = replace(space, apps=change(space.apps))
        return AppList(tuple(changed if s.number == workspace else s for s in self.workspaces))

    @staticmethod
    def _sorted(workspaces: tuple[Workspace, ...]) -> "AppList":
        return AppList(tuple(sorted(workspaces, key=lambda space: space.number)))
