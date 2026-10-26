from hiru_tsatsi.presenters.report_lines import line
from hiru_tsatsi.use_cases.offering_terminals import TerminalOffer

SUMMARY = "Work apps in a terminal"


def anything_to_say(offer: TerminalOffer) -> bool:
    return len(offer.now_opens_in_terminal) > 0 or len(offer.not_offered_again) > 0


def details(offer: TerminalOffer) -> str:
    lines = (line("Now opens in a terminal", offer.now_opens_in_terminal)
             + line("Won't be offered a terminal again", offer.not_offered_again))
    return "\n".join(lines)
