from typing import Callable, Mapping

from hiru_tsatsi.adapters.desktops.hyprctl import Run, inside_hyprland, listed, run_hyprctl
from hiru_tsatsi.adapters.desktops.lua import lua_string
from hiru_tsatsi.adapters.front_process import FrontProcess
from hiru_tsatsi.adapters.tagged_launch import TaggedLaunch
from hiru_tsatsi.adapters.terminal import in_terminal
from hiru_tsatsi.work_apps.windows import Window

Front = Callable[[int], tuple[str, str]]


def _pid(client: dict) -> int:
    return int(client.get("pid") or 0)


def _shared_pids(clients: list[dict]) -> set[int]:
    seen = set()
    shared = set()
    for client in clients:
        pid = _pid(client)
        if pid in seen:
            shared.add(pid)
        seen.add(pid)
    return shared


class Hyprland:
    def __init__(self, run: Run = run_hyprctl, tag: Callable[[], TaggedLaunch] = TaggedLaunch,
                 front: Front | None = None):
        if front is None:
            front = FrontProcess().of_window
        self.run = run
        self.tag = tag
        self.front = front

    @classmethod
    def found(cls, env: Mapping[str, str]) -> "Hyprland | None":
        if not inside_hyprland(env):
            return None
        return cls()

    def windows(self) -> list[Window]:
        clients = listed(self.run, ["clients", "-j"])
        shared = _shared_pids(clients)
        windows = []
        for client in clients:
            windows.append(self._window(client, shared))
        return windows

    def launch(self, command: str, workspace: int) -> TaggedLaunch:
        launched = self.tag()
        self._exec(launched.tagged(command), workspace)
        return launched

    def launch_in_terminal(self, command: str, workspace: int, window: str) -> None:
        self._exec(in_terminal(command, window), workspace)

    def move(self, window: Window, workspace: int) -> None:
        target = lua_string("address:" + window.address)
        self.run(["dispatch", f'hl.dsp.window.move({{ workspace = "{workspace}", follow = false, window = {target} }})'])

    def _window(self, client: dict, shared: set[int]) -> Window:
        program, folder = self._inside(_pid(client), shared)
        workspace = client.get("workspace") or {}
        return Window(str(client.get("address", "")), str(client.get("class", "")), str(client.get("title", "")),
                      int(workspace.get("id", 0)), program, folder)

    def _inside(self, pid: int, shared: set[int]) -> tuple[str, str]:
        if pid <= 0 or pid in shared:
            return "", ""
        return self.front(pid)

    def _exec(self, shell: str, workspace: int) -> None:
        self.run(["dispatch", f'hl.dsp.exec_cmd({lua_string(shell)}, {{ workspace = "{workspace} silent" }})'])
