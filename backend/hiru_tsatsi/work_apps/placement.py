import re
from dataclasses import dataclass

from hiru_tsatsi.work_apps.app import App

NOT_IN_A_WINDOW_NAME = re.compile(r"[^a-z0-9]+")


def _window_name_part(name: str) -> str:
    part = NOT_IN_A_WINDOW_NAME.sub("-", name.lower()).strip("-")
    if part == "":
        return "app"
    return part


@dataclass(frozen=True)
class Placement:
    workspace: int
    index: int
    app: App

    @property
    def terminal_window(self) -> str:
        return f"hiru-tsatsi.{self.workspace}-{self.index}-{_window_name_part(self.app.name)}"

    def as_terminal(self) -> "Placement":
        return Placement(self.workspace, self.index, self.app.opening_in_terminal(self.terminal_window))
