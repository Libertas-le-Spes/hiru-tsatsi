import json
import re
import subprocess
from typing import Callable, Mapping

from hiru_tsatsi.adapters.tagged_launch import TaggedLaunch
from hiru_tsatsi.adapters.terminal import in_terminal
from hiru_tsatsi.work_apps.windows import Window

Run = Callable[[list[str]], str]
CONTROL_CHARACTER = re.compile(r"[\x00-\x1f\x7f]")


def run_hyprctl(arguments: list[str]) -> str:
    done = subprocess.run(["hyprctl", *arguments], capture_output=True, text=True, check=False)
    return done.stdout


def lua_string(text: str) -> str:
    quoted = text.replace("\\", "\\\\").replace('"', '\\"')
    return '"' + CONTROL_CHARACTER.sub(lambda found: f"\\{ord(found.group()):03d}", quoted) + '"'


def _window(client: dict) -> Window:
    return Window(str(client.get("address", "")), str(client.get("class", "")), str(client.get("title", "")),
                  int((client.get("workspace") or {}).get("id", 0)))


class Hyprland:
    def __init__(self, run: Run = run_hyprctl, tag: Callable[[], TaggedLaunch] = TaggedLaunch):
        self.run = run
        self.tag = tag

    @classmethod
    def found(cls, env: Mapping[str, str]) -> "Hyprland | None":
        return cls() if env.get("HYPRLAND_INSTANCE_SIGNATURE") else None

    def windows(self) -> list[Window]:
        try:
            clients = json.loads(self.run(["clients", "-j"]) or "[]")
        except json.JSONDecodeError:
            return []
        return [_window(client) for client in clients if isinstance(client, dict)]

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
