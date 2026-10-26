from hiru_tsatsi.presenters.set_up_text import set_up_text
from hiru_tsatsi.use_cases.services import Services


def report_set_up(services: Services) -> int:
    print(set_up_text(services.set_up.run()))
    return 0
