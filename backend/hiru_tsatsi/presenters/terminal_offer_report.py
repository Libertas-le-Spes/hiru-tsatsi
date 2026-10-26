from hiru_tsatsi.presenters.report_lines import line
from hiru_tsatsi.use_cases.offering_terminals import TerminalOffer

SUMMARY = "Work apps in a terminal"


def anything_to_say(offer: TerminalOffer) -> bool:
    told = offer.now_opens_in_terminal + offer.not_offered_again + offer.window_found_after_all
    return len(told) > 0


def details(offer: TerminalOffer) -> str:
    lines = (line("Now opens in a terminal", offer.now_opens_in_terminal)
             + line("Won't be offered a terminal again", offer.not_offered_again)
             + line("Its window came after all", offer.window_found_after_all))
    return "\n".join(lines)
