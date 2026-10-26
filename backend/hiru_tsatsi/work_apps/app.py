from dataclasses import dataclass, replace

from hiru_tsatsi.work_apps.refusals import required
from hiru_tsatsi.work_apps.terminal_use import TerminalUse


@dataclass(frozen=True)
class App:
    name: str
    command: str
    learned_window: str = ""
    terminal: TerminalUse = TerminalUse.NOT_KNOWN

    @property
    def opens_in_terminal(self) -> bool:
        return self.terminal == TerminalUse.OPENS_IN_ONE

    @property
    def terminal_ruled_out(self) -> bool:
        return self.terminal == TerminalUse.RULED_OUT

    @property
    def knows_window(self) -> bool:
        return self.learned_window.strip() != ""

    def checked(self) -> "App":
        return replace(self, name=required("name", self.name), command=required("command", self.command))

    def changed(self, name: str, command: str) -> "App":
        changed = replace(self, name=name, command=command).checked()
        if changed.command == self.command:
            return changed
        return App(changed.name, changed.command)

    def knowing_window(self, window: str) -> "App":
        if self.opens_in_terminal:
            return replace(self, learned_window=window, terminal=TerminalUse.NOT_KNOWN)
        return replace(self, learned_window=window)

    def opening_in_terminal(self, window: str) -> "App":
        return replace(self, learned_window=window, terminal=TerminalUse.OPENS_IN_ONE)

    def never_in_terminal(self) -> "App":
        return replace(self, terminal=TerminalUse.RULED_OUT)
