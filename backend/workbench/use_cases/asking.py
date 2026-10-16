from workbench.use_cases.ports import Notifier
from workbench.use_cases.starting import Outcome, StartApps

QUESTION = "Start your work apps?"
EXPLANATION = "Opens each of them on its own workspace. Click to start."
ACTION = "Start work apps"


class AskToStart:
    def __init__(self, notifier: Notifier, start: StartApps):
        self.notifier = notifier
        self.start = start

    def run(self) -> Outcome | None:
        return self.start.run() if self.notifier.ask(QUESTION, EXPLANATION, ACTION) else None
