import posixpath
from dataclasses import dataclass

from hiru_tsatsi.use_cases.failures import NotOurs
from hiru_tsatsi.use_cases.ports import CommandLinks


@dataclass(frozen=True)
class Linked:
    command: str
    short: str
    retired: str | None


class LinkCommands:
    def __init__(self, links: CommandLinks, bin_dir: str, launcher: str):
        self.links = links
        self.launcher = launcher
        self.command = posixpath.join(bin_dir, "hiru-tsatsi")
        self.short = posixpath.join(bin_dir, "tsatsi")
        self.old_short = posixpath.join(bin_dir, "hiru")

    def run(self) -> Linked:
        self._refuse_another_tool(self.command)
        self._refuse_another_tool(self.short)
        retired = self._retire_old_short_name()
        self.links.link(self.command, self.launcher)
        self.links.link(self.short, self.launcher)
        return Linked(self.command, self.short, retired)

    def _refuse_another_tool(self, path: str) -> None:
        if self.links.present(path) and not self.links.is_ours(path):
            raise NotOurs(path)

    def _retire_old_short_name(self) -> str | None:
        if not self.links.is_ours(self.old_short):
            return None
        self.links.remove(self.old_short)
        return self.old_short
