import unittest
from unittest.mock import create_autospec

from hiru_tsatsi.presenters.starting_notice import StartingNotice
from hiru_tsatsi.use_cases.ports import Notifier


class SayingWhichAppsAreStarting(unittest.TestCase):
    def test_one_app(self):
        notifier = create_autospec(Notifier, instance=True)
        StartingNotice(notifier).announce(["Steam"])
        notifier.notify.assert_called_once_with("Starting 1 work app", "Steam")

    def test_several_apps(self):
        notifier = create_autospec(Notifier, instance=True)
        StartingNotice(notifier).announce(["Harbour", "Lantern"])
        notifier.notify.assert_called_once_with("Starting 2 work apps", "Harbour, Lantern")


if __name__ == "__main__":
    unittest.main()
