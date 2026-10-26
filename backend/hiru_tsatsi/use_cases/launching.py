from hiru_tsatsi.use_cases.ports import Desktop, Launch, Launches, Terminal
from hiru_tsatsi.work_apps.placement import Placement


class Launcher:
    def __init__(self, desktop: Desktop, launches: Launches, terminal: Terminal):
        self.desktop = desktop
        self.launches = launches
        self.terminal = terminal

    def plainly(self, placement: Placement) -> None:
        self.desktop.launch(placement.app.command, placement.workspace)

    def watched(self, placement: Placement) -> Launch:
        launch = self.launches.new()
        self.desktop.launch(launch.wrapped(placement.app.command), placement.workspace)
        return launch

    def in_terminal(self, placement: Placement) -> None:
        app = placement.app
        self.desktop.launch(self.terminal.wrapped(app.command, app.learned_window), placement.workspace)
