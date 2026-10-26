import shlex
from dataclasses import dataclass

from hiru_tsatsi.use_cases.ports import DesktopSetUp
from hiru_tsatsi.work_apps.shortcut import PREFERRED, Keys, first_free


@dataclass(frozen=True)
class SetUp:
    keys: Keys | None
    kept: bool


class SetUpDesktop:
    def __init__(self, desktop: DesktopSetUp, command: str):
        self.desktop = desktop
        self.command = command

    def run(self) -> SetUp:
        kept = self.desktop.installed_keys()
        keys = kept or first_free(PREFERRED, self.desktop.taken_keys())
        command = shlex.quote(self.command)
        self.desktop.install(keys, f"{command} start", f"{command} ask")
        return SetUp(keys, kept is not None)
