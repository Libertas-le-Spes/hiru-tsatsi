import json
import re
from pathlib import Path
from typing import Mapping

from hiru_tsatsi.adapters.desktops.hyprland import Run, lua_string, run_hyprctl
from hiru_tsatsi.adapters.storage.atomic_file import NotWritten, text_or_nothing, write_atomically
from hiru_tsatsi.use_cases.ports import ConfigLeftAlone, SetUpFailed
from hiru_tsatsi.work_apps.shortcut import Keys

MODIFIER_BITS = {"SHIFT": 1, "CTRL": 4, "ALT": 8, "SUPER": 64}
BOUND_KEYS = re.compile(r'hl\.bind\("([^"]+)"')


def keys_from_bind(bind: dict) -> Keys:
    mask = int(bind.get("modmask", 0))
    return Keys(frozenset(name for name, bit in MODIFIER_BITS.items() if mask & bit), str(bind.get("key", "")).upper())


def _with_line_added(text: str, line: str) -> str:
    if text != "" and not text.endswith("\n"):
        text = text + "\n"
    return text + line + "\n"


class HyprlandSetUp:
    def __init__(self, config_folder: Path, run: Run = run_hyprctl):
        self.own_file = config_folder / "hiru-tsatsi.lua"
        self.main_file = config_folder / "hyprland.lua"
        self.run = run

    @classmethod
    def found(cls, env: Mapping[str, str], config_home: Path) -> "HyprlandSetUp | None":
        return cls(config_home / "hypr") if env.get("HYPRLAND_INSTANCE_SIGNATURE") else None

    def installed_keys(self) -> Keys | None:
        bound = BOUND_KEYS.search(self.own_file.read_text()) if self.own_file.exists() else None
        return Keys.parse(bound.group(1)) if bound else None

    def taken_keys(self) -> set[Keys]:
        try:
            binds = json.loads(self.run(["binds", "-j"]) or "[]")
        except json.JSONDecodeError:
            return set()
        return {keys_from_bind(bind) for bind in binds if isinstance(bind, dict) and not bind.get("submap")}

    def install(self, keys: Keys | None, start_command: str, ask_command: str) -> None:
        try:
            write_atomically(self.own_file, self._own_config(keys, start_command, ask_command))
            self._load_from_main_file()
        except NotWritten as refused:
            raise ConfigLeftAlone(str(refused)) from refused
        self.run(["reload"])
        errors = self.run(["configerrors"]).strip()
        if errors:
            raise SetUpFailed(errors)

    @staticmethod
    def _own_config(keys: Keys | None, start_command: str, ask_command: str) -> str:
        bind = (f'hl.bind({lua_string(keys.text())}, hl.dsp.exec_cmd({lua_string(start_command)}), '
                f'{{ description = "Start work apps" }})\n') if keys else ""
        return bind + f'hl.on("hyprland.start", function()\n  hl.exec_cmd({lua_string(ask_command)})\nend)\n'

    def _load_from_main_file(self) -> None:
        line = f"dofile({lua_string(str(self.own_file))})"
        current = text_or_nothing(self.main_file)
        if line in current:
            return
        write_atomically(self.main_file, _with_line_added(current, line), read_before=current)
