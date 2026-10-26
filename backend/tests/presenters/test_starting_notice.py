import unittest

from tests.fakes.notifying import FakeNotifier
from hiru_tsatsi.presenters.starting_notice import StartingNotice


class SayingWhichAppsAreStarting(unittest.TestCase):
    def test_one_app(self):
        notifier = FakeNotifier()
        StartingNotice(notifier).announce(["Steam"])
        self.assertEqual(notifier.sent, [("Starting 1 work app", "Steam")])

    def test_several_apps(self):
        notifier = FakeNotifier()
        StartingNotice(notifier).announce(["Main", "Review"])
        self.assertEqual(notifier.sent, [("Starting 2 work apps", "Main, Review")])


if __name__ == "__main__":
    unittest.main()
