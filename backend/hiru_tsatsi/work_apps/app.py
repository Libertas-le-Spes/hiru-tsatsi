from dataclasses import dataclass, replace

from hiru_tsatsi.work_apps.refusals import required


@dataclass(frozen=True)
class App:
    name: str
    command: str
    learned_window: str = ""

    @property
    def knows_window(self) -> bool:
        return self.learned_window.strip() != ""

    def checked(self) -> "App":
        return replace(self, name=required("name", self.name), command=required("command", self.command))

    def changed(self, name: str, command: str) -> "App":
        changed = replace(self, name=name, command=command).checked()
        if changed.command == self.command:
            return changed
        return changed.knowing_window("")

    def knowing_window(self, window: str) -> "App":
        return replace(self, learned_window=window)
