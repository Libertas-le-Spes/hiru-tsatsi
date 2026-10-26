from hiru_tsatsi.use_cases.offering_terminals import TerminalOffer

SUMMARY = "Work apps in a terminal"


def _line(label: str, names: list[str]) -> list[str]:
    if not names:
        return []
    return [f"{label}: {', '.join(names)}"]


def anything_to_say(offer: TerminalOffer) -> bool:
    return len(offer.now_opens_in_terminal) > 0 or len(offer.not_offered_again) > 0


def details(offer: TerminalOffer) -> str:
    lines = (_line("Now opens in a terminal", offer.now_opens_in_terminal)
             + _line("Won't be offered a terminal again", offer.not_offered_again))
    return "\n".join(lines)
