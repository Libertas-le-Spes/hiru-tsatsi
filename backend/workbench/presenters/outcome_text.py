from workbench.use_cases.starting import Outcome


def _line(label: str, names: list[str]) -> list[str]:
    return [f"{label}: {', '.join(names)}"] if names else []


def summary(outcome: Outcome) -> str:
    if not outcome.started and not outcome.already_open:
        return "No work apps are set up yet"
    return f"Started {len(outcome.started)}, {len(outcome.already_open)} already open"


def not_supported(desktop: str) -> str:
    return (f"Workbench can't place windows on {desktop} yet, so it started nothing. "
            "Apps opened without being put on their workspaces would only need sorting by hand.")


def details(outcome: Outcome) -> str:
    lines = (_line("Started", outcome.started) + _line("Already open", outcome.already_open)
             + _line("Moved to their workspace", outcome.moved)
             + _line("No window seen within a minute", outcome.unseen))
    return "\n".join(lines)
