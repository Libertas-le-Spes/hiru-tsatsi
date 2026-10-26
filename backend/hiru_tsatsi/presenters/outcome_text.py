from hiru_tsatsi.use_cases.outcome import Outcome
from hiru_tsatsi.use_cases.setting_up import SetUp


def _line(label: str, names: list[str]) -> list[str]:
    if not names:
        return []
    return [f"{label}: {', '.join(names)}"]


def summary(outcome: Outcome) -> str:
    if not outcome.started and not outcome.already_open:
        return "No work apps are set up yet"
    return f"Started {len(outcome.started)}, {len(outcome.already_open)} already open"


def not_supported(desktop: str) -> str:
    return (f"Hiru Tsatsi can't place windows on {desktop} yet, so it started nothing. "
            "Apps opened without being put on their workspaces would only need sorting by hand.")


def details(outcome: Outcome) -> str:
    lines = (_line("Started", outcome.started) + _line("Already open", outcome.already_open)
             + _line("Moved to their workspace", outcome.moved)
             + _line("Opened in a terminal, as they need one", outcome.in_terminal)
             + _line("No window seen within a minute", outcome.unseen))
    return "\n".join(lines)


UNCHOSEN_REASON = {True: "because window-names is installed", False: "because window-names isn't installed"}


def _on_or_off(on: bool) -> str:
    if on:
        return "on"
    return "off"


def _why(on: bool, chosen: bool) -> str:
    if chosen:
        return "as you chose"
    return UNCHOSEN_REASON[on]


def window_titles_text(on: bool, chosen: bool) -> str:
    return (f"Window titles are {_on_or_off(on)}, {_why(on, chosen)}. "
            "Turn them on or off with `hiru-tsatsi window-titles on` or `off`.")


def _starts(kept: bool) -> str:
    if kept:
        return "still starts"
    return "now starts"


def set_up_text(set_up: SetUp) -> str:
    asked = "At login, a notification asks whether to start your work apps."
    if set_up.keys is None:
        return f"Every shortcut Hiru Tsatsi would pick is taken, so none was added; bind `hiru-tsatsi start` yourself. {asked}"
    return f"{set_up.keys.text()} {_starts(set_up.kept)} your work apps. {asked}"
