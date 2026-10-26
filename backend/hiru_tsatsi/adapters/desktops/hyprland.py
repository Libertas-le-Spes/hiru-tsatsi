from typing import Callable, Mapping

from hiru_tsatsi.adapters.desktops.hyprctl import Run, inside_hyprland, listed, run_hyprctl
from hiru_tsatsi.adapters.desktops.lua import lua_string
from hiru_tsatsi.adapters.front_process import FrontProcess
from hiru_tsatsi.adapters.tagged_launch import TaggedLaunch
from hiru_tsatsi.adapters.terminal import in_terminal
from hiru_tsatsi.work_apps.windows import Window


class Hyprland:
    def __init__(self, run: Run = run_hyprctl, tag: Callable[[], TaggedLaunch] = TaggedLaunch,
                 front: Callable[[int], tuple[str, str]] = FrontProcess().of_window):
        self.run = run
        self.tag = tag
        self.front = front

    @classmethod
    def found(cls, env: Mapping[str, str]) -> "Hyprland | None":
        if not inside_hyprland(env):
            return None
        return cls()

    def windows(self) -> list[Window]:
        windows = []
        for client in listed(self.run, ["clients", "-j"]):
            windows.append(self._window(client))
        return windows

    def _window(self, client: dict) -> Window:
        program, folder = self.front(int(client.get("pid") or 0))
        return Window(str(client.get("address", "")), str(client.get("class", "")), str(client.get("title", "")),
                      int((client.get("workspace") or {}).get("id", 0)), program, folder)

    def launch(self, command: str, workspace: int) -> TaggedLaunch:
        launched = self.tag()
        self._exec(launched.tagged(command), workspace)
        return launched

    def launch_in_terminal(self, command: str, workspace: int, window: str) -> None:
        self._exec(in_terminal(command, window), workspace)

    def _exec(self, shell: str, workspace: int) -> None:
        self.run(["dispatch", f'hl.dsp.exec_cmd({lua_string(shell)}, {{ workspace = "{workspace} silent" }})'])

    def move(self, window: Window, workspace: int) -> None:
        target = lua_string("address:" + window.address)
        self.run(["dispatch", f'hl.dsp.window.move({{ workspace = "{workspace}", follow = false, window = {target} }})'])
