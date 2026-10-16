import json
import subprocess
from typing import Callable, Mapping

from workbench.work_apps.windows import Window

Run = Callable[[list[str]], str]


def run_hyprctl(arguments: list[str]) -> str:
    done = subprocess.run(["hyprctl", *arguments], capture_output=True, text=True, check=False)
    return done.stdout


def _lua_string(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _window(client: dict) -> Window:
    return Window(str(client.get("address", "")), str(client.get("class", "")), str(client.get("title", "")),
                  int((client.get("workspace") or {}).get("id", 0)))


class Hyprland:
    def __init__(self, run: Run = run_hyprctl):
        self.run = run

    @classmethod
    def found(cls, env: Mapping[str, str]) -> "Hyprland | None":
        return cls() if env.get("HYPRLAND_INSTANCE_SIGNATURE") else None

    def windows(self) -> list[Window]:
        try:
            clients = json.loads(self.run(["clients", "-j"]) or "[]")
        except json.JSONDecodeError:
            return []
        return [_window(client) for client in clients if isinstance(client, dict)]

    def launch(self, command: str, workspace: int) -> None:
        self.run(["dispatch", f'hl.dsp.exec_cmd({_lua_string(command)}, {{ workspace = "{workspace} silent" }})'])

    def move(self, window: Window, workspace: int) -> None:
        target = _lua_string("address:" + window.address)
        self.run(["dispatch", f'hl.dsp.window.move({{ workspace = "{workspace}", follow = false, window = {target} }})'])
