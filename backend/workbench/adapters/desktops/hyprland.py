import json
import subprocess
from typing import Callable, Mapping, Protocol

from workbench.work_apps.windows import Window

Run = Callable[[list[str]], str]


def run_hyprctl(arguments: list[str]) -> str:
    done = subprocess.run(["hyprctl", *arguments], capture_output=True, text=True, check=False)
    return done.stdout


def _lua_string(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


class Dialect(Protocol):
    def understood(self, run: Run) -> bool: ...

    def launch(self, command: str, workspace: int) -> str: ...

    def move(self, address: str, workspace: int) -> str: ...


class LuaDialect:
    def understood(self, run: Run) -> bool:
        return run(["dispatch", 'hl.dsp.exec_cmd("true")']).strip() == "ok"

    def launch(self, command: str, workspace: int) -> str:
        return f'hl.dsp.exec_cmd({_lua_string(command)}, {{ workspace = "{workspace} silent" }})'

    def move(self, address: str, workspace: int) -> str:
        return f'hl.dsp.window.move({{ workspace = "{workspace}", follow = false, window = {_lua_string("address:" + address)} }})'


class ClassicDialect:
    def understood(self, run: Run) -> bool:
        return run(["dispatch", "exec", "true"]).strip() == "ok"

    def launch(self, command: str, workspace: int) -> str:
        return f"exec [workspace {workspace} silent] {command}"

    def move(self, address: str, workspace: int) -> str:
        return f"movetoworkspacesilent {workspace},address:{address}"


DIALECTS: list[Dialect] = [LuaDialect(), ClassicDialect()]


def _window(client: dict) -> Window:
    return Window(str(client.get("address", "")), str(client.get("class", "")), str(client.get("title", "")),
                  int((client.get("workspace") or {}).get("id", 0)))


class Hyprland:
    sees_windows = True

    def __init__(self, dialect: Dialect, run: Run = run_hyprctl):
        self.dialect = dialect
        self.run = run

    @classmethod
    def found(cls, env: Mapping[str, str], run: Run = run_hyprctl) -> "Hyprland | None":
        if not env.get("HYPRLAND_INSTANCE_SIGNATURE"):
            return None
        dialect = next((d for d in DIALECTS if d.understood(run)), None)
        return cls(dialect, run) if dialect else None

    def windows(self) -> list[Window]:
        try:
            clients = json.loads(self.run(["clients", "-j"]) or "[]")
        except json.JSONDecodeError:
            return []
        return [_window(client) for client in clients if isinstance(client, dict)]

    def launch(self, command: str, workspace: int) -> None:
        self.run(["dispatch", self.dialect.launch(command, workspace)])

    def move(self, window: Window, workspace: int) -> None:
        self.run(["dispatch", self.dialect.move(window.address, workspace)])
