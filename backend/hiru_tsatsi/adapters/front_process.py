from hiru_tsatsi.adapters.proc_files import ProcFiles

SHELLS = {"sh", "dash", "bash", "zsh", "fish"}
DEEPEST = 8


class FrontProcess:
    def __init__(self, processes: ProcFiles | None = None):
        if processes is None:
            processes = ProcFiles()
        self.processes = processes

    def of_window(self, pid: int) -> tuple[str, str]:
        children = self.processes.children(pid)
        if len(children) != 1:
            return "", ""
        front = self._past_waiting_shells(self._in_front(children[0]))
        return self.processes.program(front), self.processes.folder(front)

    def _in_front(self, shell: int) -> int:
        group = self.processes.foreground_group(shell)
        if group <= 0:
            return shell
        return group

    def _past_waiting_shells(self, pid: int) -> int:
        for _ in range(DEEPEST):
            children = self.processes.children(pid)
            if self.processes.program(pid) not in SHELLS or not children:
                return pid
            pid = children[0]
        return pid
