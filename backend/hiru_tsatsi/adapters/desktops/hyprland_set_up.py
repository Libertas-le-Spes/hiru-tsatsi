import re
import shlex
from pathlib import Path
from typing import Mapping

from hiru_tsatsi.adapters.desktops.hyprctl import Run, inside_hyprland, run_hyprctl
from hiru_tsatsi.adapters.desktops.hyprland_binds import taken_keys
from hiru_tsatsi.adapters.desktops.lua import lua_string
from hiru_tsatsi.adapters.storage.files import Disk, Files
from hiru_tsatsi.use_cases.failures import SetUpFailed
from hiru_tsatsi.work_apps.shortcut import Keys

BOUND_KEYS = re.compile(r'hl\.bind\("([^"]+)"')


def _shortcut_line(keys: Keys | None, start_command: str) -> str:
    if keys is None:
        return ""
    return (f'hl.bind({lua_string(keys.text())}, hl.dsp.exec_cmd({lua_string(start_command)}), '
            f'{{ description = "Start work apps" }})\n')


def _login_question(ask_command: str) -> str:
    return f'hl.on("hyprland.start", function()\n  hl.exec_cmd({lua_string(ask_command)})\nend)\n'


def _with_line_added(text: str, line: str) -> str:
    if text != "" and not text.endswith("\n"):
        text = text + "\n"
    return text + line + "\n"


class HyprlandSetUp:
    def __init__(self, config_folder: Path, files: Files, run: Run = run_hyprctl):
        self.own_file = config_folder / "hiru-tsatsi.lua"
        self.main_file = config_folder / "hyprland.lua"
        self.run = run
        self.files = files

    @classmethod
    def found(cls, env: Mapping[str, str], config_home: Path) -> "HyprlandSetUp | None":
        if not inside_hyprland(env):
            return None
        return cls(config_home / "hypr", Disk())

    def installed_keys(self) -> Keys | None:
        bound = BOUND_KEYS.search(self.files.read(self.own_file))
        if bound is None:
            return None
        return Keys.parse(bound.group(1))

    def taken_keys(self) -> set[Keys]:
        return taken_keys(self.run)

    def install(self, keys: Keys | None, command: str) -> None:
        self.files.write(self.own_file, self._own_config(keys, shlex.quote(command)), follow_link=True)
        self._load_from_main_file()
        self.run(["reload"])
        errors = self.run(["configerrors"]).strip()
        if errors:
            raise SetUpFailed(errors)

    @staticmethod
    def _own_config(keys: Keys | None, command: str) -> str:
        return _shortcut_line(keys, f"{command} start") + _login_question(f"{command} ask")

    def _load_from_main_file(self) -> None:
        line = f"dofile({lua_string(str(self.own_file))})"
        current = self.files.read(self.main_file)
        if line in current:
            return
        self.files.write(self.main_file, _with_line_added(current, line), read_before=current, follow_link=True)
