from hiru_tsatsi.presenters.report_lines import line
from hiru_tsatsi.use_cases.outcome import Outcome


def summary(outcome: Outcome) -> str:
    if not outcome.started and not outcome.already_open:
        return "No work apps are set up yet"
    return f"Started {len(outcome.started)}, {len(outcome.already_open)} already open"


def details(outcome: Outcome) -> str:
    lines = (line("Started", outcome.started) + line("Already open", outcome.already_open)
             + line("Moved to their workspace", outcome.moved)
             + line("No window seen within a minute", outcome.unseen)
             + line("Stopped without a window", outcome.stopped_without_window))
    return "\n".join(lines)
