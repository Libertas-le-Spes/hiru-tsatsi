import sys

from hiru_tsatsi.use_cases.failures import Failure
from hiru_tsatsi.work_apps.refusals import Refused

STOPS = (Failure, Refused)


def report_failure(failure: Failure | Refused) -> int:
    print(failure.explained(), file=sys.stderr)
    return failure.exit_code
