from typing import Mapping

from hiru_tsatsi.adapters.desktops.hyprctl import Run, inside_hyprland, listed, run_hyprctl
from hiru_tsatsi.adapters.desktops.lua import lua_string
from hiru_tsatsi.work_apps.windows import Window


def _window(client: dict) -> Window:
    workspace = client.get("workspace") or {}
    return Window(str(client.get("address", "")), str(client.get("class", "")), str(client.get("title", "")),
                  int(workspace.get("id", 0)))


class Hyprland:
    def __init__(self, run: Run = run_hyprctl):
        self.run = run

    @classmethod
    def found(cls, env: Mapping[str, str]) -> "Hyprland | None":
        if not inside_hyprland(env):
            return None
        return cls()

    def windows(self) -> list[Window]:
        windows = []
        for client in listed(self.run, ["clients", "-j"]):
            windows.append(_window(client))
        return windows

    def launch(self, command: str, workspace: int) -> None:
        self.run(["dispatch", f'hl.dsp.exec_cmd({lua_string(command)}, {{ workspace = "{workspace} silent" }})'])

    def move(self, window: Window, workspace: int) -> None:
        target = lua_string("address:" + window.address)
        moving = f'hl.dsp.window.move({{ workspace = "{workspace}", follow = false, window = {target} }})'
        self.run(["dispatch", moving])
