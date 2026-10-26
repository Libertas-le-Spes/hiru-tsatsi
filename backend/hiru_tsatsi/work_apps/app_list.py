from dataclasses import dataclass, replace

from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.refusals import NothingThere, NumberTaken, required
from hiru_tsatsi.work_apps.workspace import Workspace


def _by_number(space: Workspace) -> int:
    return space.number


@dataclass(frozen=True)
class AppList:
    workspaces: tuple[Workspace, ...] = ()

    def placements(self) -> list[Placement]:
        placements = []
        for space in self.workspaces:
            for index, app in enumerate(space.apps):
                placements.append(Placement(space.number, index, app))
        return placements

    def placement(self, workspace: int, index: int) -> Placement:
        apps = self.workspace(workspace).apps
        if not 0 <= index < len(apps):
            raise NothingThere()
        return Placement(workspace, index, apps[index])

    def workspace(self, number: int) -> Workspace:
        found = self._workspace_numbered(number)
        if found is None:
            raise NothingThere()
        return found

    def has_workspace(self, number: int) -> bool:
        return self._workspace_numbered(number) is not None

    def _workspace_numbered(self, number: int) -> Workspace | None:
        for space in self.workspaces:
            if space.number == number:
                return space
        return None

    def with_workspace(self, number: int, label: str) -> "AppList":
        self._refuse_taken_number(number)
        return self._sorted(self.workspaces + (Workspace(number, required("label", label)),))

    def with_workspace_changed(self, number: int, new_number: int, label: str) -> "AppList":
        space = self.workspace(number)
        if new_number != number:
            self._refuse_taken_number(new_number)
        changed = replace(space, number=new_number, label=required("label", label))
        return self._sorted(self._with_workspace_swapped(number, changed))

    def without_workspace(self, number: int) -> "AppList":
        self.workspace(number)
        kept = []
        for space in self.workspaces:
            if space.number != number:
                kept.append(space)
        return AppList(tuple(kept))

    def with_app(self, workspace: int, app: App) -> "AppList":
        space = self.workspace(workspace)
        return AppList(self._with_workspace_swapped(workspace, space.with_app_added(app.checked())))

    def with_app_changed(self, workspace: int, index: int, name: str, command: str) -> "AppList":
        current = self.placement(workspace, index)
        return self._with_app_at(current, current.app.renamed(name, command))

    def without_app(self, workspace: int, index: int) -> "AppList":
        self.placement(workspace, index)
        space = self.workspace(workspace)
        return AppList(self._with_workspace_swapped(workspace, space.without_app(index)))

    def with_learned_window(self, placement: Placement, window: str) -> "AppList":
        current = self.placement(placement.workspace, placement.index)
        return self._with_app_at(current, current.app.knowing_window(window))

    def with_app_replaced(self, placement: Placement, app: App) -> "AppList":
        current = self.placement(placement.workspace, placement.index)
        return self._with_app_at(current, app)

    def with_terminal(self, placement: Placement) -> "AppList":
        current = self.placement(placement.workspace, placement.index)
        return self._with_app_at(current, current.as_terminal().app)

    def _refuse_taken_number(self, number: int) -> None:
        if number < 1 or self.has_workspace(number):
            raise NumberTaken(number)

    def _with_app_at(self, placement: Placement, app: App) -> "AppList":
        space = self.workspace(placement.workspace)
        return AppList(self._with_workspace_swapped(placement.workspace, space.with_app_replaced(placement.index, app)))

    def _with_workspace_swapped(self, number: int, changed: Workspace) -> tuple[Workspace, ...]:
        swapped = []
        for space in self.workspaces:
            if space.number == number:
                swapped.append(changed)
            else:
                swapped.append(space)
        return tuple(swapped)

    @staticmethod
    def _sorted(workspaces: tuple[Workspace, ...]) -> "AppList":
        return AppList(tuple(sorted(workspaces, key=_by_number)))
