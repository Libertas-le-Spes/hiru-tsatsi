from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.ports import Notifier
from hiru_tsatsi.use_cases.starting import StartApps

QUESTION = "Start your work apps?"
EXPLANATION = "Opens each of them on its own workspace. Click to start."
ACTION = "Start work apps"


class AskToStart:
    def __init__(self, notifier: Notifier, start: StartApps):
        self.notifier = notifier
        self.start = start

    def run(self) -> Outcome | None:
        if not self.notifier.ask(QUESTION, EXPLANATION, ACTION):
            return None
        return self.start.run()
