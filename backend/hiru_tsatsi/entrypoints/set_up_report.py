import sys

from hiru_tsatsi.presenters.set_up_text import set_up_text
from hiru_tsatsi.use_cases.failures import NotSaved, SetUpFailed
from hiru_tsatsi.use_cases.services import Services


def report_set_up(services: Services) -> int:
    try:
        print(set_up_text(services.set_up.run()))
    except SetUpFailed as failed:
        print(f"The desktop reported a problem after setting up, so check its config:\n{failed}", file=sys.stderr)
        return 1
    except NotSaved as refused:
        print(f"Nothing was set up: {refused}.", file=sys.stderr)
        return 1
    return 0
