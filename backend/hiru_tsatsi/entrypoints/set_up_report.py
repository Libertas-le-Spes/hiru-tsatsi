from hiru_tsatsi.presenters.outcome_text import set_up_text
from hiru_tsatsi.use_cases.ports import ConfigLeftAlone, SetUpFailed
from hiru_tsatsi.wiring import Services


def report_set_up(services: Services) -> int:
    try:
        print(set_up_text(services.set_up.run()))
    except SetUpFailed as failed:
        print(f"The desktop reported a problem after setting up, so check its config:\n{failed}")
        return 1
    except ConfigLeftAlone as refused:
        print(f"Nothing was set up: {refused}.")
        return 1
    return 0
